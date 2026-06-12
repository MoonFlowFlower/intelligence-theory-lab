import copy
import importlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TASK_ID = "EGO-MAINLINE-ADMISSION-EXECUTION-001A"
ARTIFACT_DIR = ROOT / "artifacts" / "ego_mainline_admission_execution_001a"
DOC = ROOT / "docs" / "codex" / "tasks" / f"{TASK_ID}.md"

REQUIRED_ARTIFACTS = {
    "result.json",
    "parent_boundary_readback.json",
    "admission_contract_evaluation.json",
    "post_bridge_caveat_revalidation.json",
    "actionability_revalidation.json",
    "computed_evidence_provenance.json",
    "negative_evidence_handling.json",
    "forbidden_claims_and_actions.json",
    "admission_decision_trace.json",
    "ablation_report.json",
    "authorization_flags.json",
    "claim_ceiling.txt",
}

AUTHORIZATION_FLAGS = {
    "authorize_gate4",
    "authorize_bridge_runtime",
    "authorize_ego_runtime",
    "authorize_companion_behavior",
    "authorize_llm_rag",
    "authorize_user_model",
    "authorize_relationship_or_emotion",
    "authorize_personalization",
    "authorize_architecture_implementation",
    "authorize_mechanism_validity_claim",
    "authorize_runtime_correctness_claim",
}

FORBIDDEN_VERDICTS = {
    "EGO ready",
    "bridge ready",
    "runtime ready",
    "Gate4 authorized",
    "mechanism proven",
    "architecture valid",
    "agency proven",
    "selfhood proven",
    "consciousness proven",
    "companion authorized",
    "relationship/emotion learning proven",
}

WHAT_THIS_DOES_NOT_PROVE = {
    "EGO readiness",
    "bridge readiness",
    "runtime readiness",
    "Gate4 readiness",
    "mechanism validity",
    "theory validity",
    "architecture correctness",
    "agency",
    "selfhood",
    "consciousness",
    "emotion",
    "relationship learning",
    "stable user benefit",
    "future runtime correctness",
    "runtime authorization",
}

NEGATIVE_CONTROLS = {
    "missing_preflight_001a_anchor": "validate_parent_boundaries",
    "missing_alignment_001a_anchor": "validate_parent_boundaries",
    "missing_post_bridge_001d_verdict_caveat_claim_ceiling": "validate_post_bridge_caveats",
    "blocked_old_canonicalization_001a_used_as_parent": "validate_parent_boundaries",
    "authorization_flag_true": "validate_authorization_flags",
    "static_pass_without_callable_gate_logic": "validate_computed_verdict_source",
    "copied_45_row_matrix_or_duplicate_schema": "validate_duplicate_schema_and_matrix",
    "negative_001b_001c_upgraded_to_positive_downstream_evidence": "validate_negative_evidence_handling",
    "post_bridge_001d_caveat_removed": "validate_post_bridge_caveats",
    "runtime_gate4_ego_authorization_claim_inserted": "validate_forbidden_claims_and_actions",
}


def _runner():
    return importlib.import_module("ego_mainline_admission_execution_001a.runner")


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _walk(value, path="$"):
    rows = [(path, value)]
    if isinstance(value, dict):
        for key, item in value.items():
            rows.extend(_walk(item, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            rows.extend(_walk(item, f"{path}[{index}]"))
    return rows


def test_materialized_required_outputs_exist_parse_and_have_provenance():
    runner = _runner()

    assert DOC.exists()
    assert ARTIFACT_DIR.exists()
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})
    assert (ARTIFACT_DIR / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == runner.CLAIM_CEILING

    for name in REQUIRED_ARTIFACTS - {"claim_ceiling.txt"}:
        payload = _read_json(ARTIFACT_DIR / name)
        assert isinstance(payload, dict)
        meta = payload.get("computed_evidence_provenance")
        assert meta
        assert meta["producer_function"]
        assert meta["input_artifacts"]
        assert meta["input_commits_tags_refs"]
        assert meta["run_id"]
        assert meta["aggregation_rule"]
        assert meta["code_path_hash"]
        assert "gate_outcomes" in meta
        assert "failure_reasons" in meta


def test_parent_boundaries_resolve_exactly_and_exclude_blocked_old_001a():
    runner = _runner()
    parents = _read_json(ARTIFACT_DIR / "parent_boundary_readback.json")
    rows = {row["boundary_id"]: row for row in parents["parent_boundaries"]}

    expected = {
        "preflight_001a": (runner.PREFLIGHT_001A_COMMIT, runner.PREFLIGHT_001A_TAG),
        "alignment_001a": (runner.ALIGNMENT_001A_COMMIT, runner.ALIGNMENT_001A_TAG),
        "admission_coverage_reference_001a": (
            runner.COVERAGE_REFERENCE_001A_COMMIT,
            runner.COVERAGE_REFERENCE_001A_TAG,
        ),
        "canonicalization_provenance_repair_001b": (
            runner.CANONICALIZATION_REPAIR_001B_COMMIT,
            runner.CANONICALIZATION_REPAIR_001B_TAG,
        ),
        "coverage_compression_001d": (runner.COVERAGE_COMPRESSION_001D_COMMIT, runner.COVERAGE_COMPRESSION_001D_TAG),
        "post_bridge_admission_executable_001d": (runner.POST_BRIDGE_001D_COMMIT, None),
        "prior_readiness_audit_reference_only": (runner.PRIOR_READINESS_AUDIT_COMMIT, None),
    }
    assert set(rows) == set(expected)
    for boundary_id, (commit, tag) in expected.items():
        assert rows[boundary_id]["expected_commit"] == commit
        assert rows[boundary_id]["remote_tag"] == tag
        assert rows[boundary_id]["path_last_commit"] == commit
        assert rows[boundary_id]["resolved_exactly"] is True

    assert rows["preflight_001a"]["remote_resolved_commit"] == runner.PREFLIGHT_001A_COMMIT
    assert rows["alignment_001a"]["remote_resolved_commit"] == runner.ALIGNMENT_001A_COMMIT
    assert rows["canonicalization_provenance_repair_001b"]["expected_commit"] != runner.BLOCKED_OLD_CANONICALIZATION_001A_COMMIT
    assert parents["blocked_old_canonicalization_001a"]["used_as_parent"] is False
    assert parents["all_required_boundaries_resolved"] is True
    assert parents["all_required_remote_anchors_verified"] is True


def test_admission_contract_evaluation_runs_all_callable_gates():
    evaluation = _read_json(ARTIFACT_DIR / "admission_contract_evaluation.json")
    observed = {row["validator"]: row for row in evaluation["gate_outcomes"]}
    expected = {
        "validate_parent_boundaries",
        "validate_remote_anchors",
        "validate_alignment_contract",
        "validate_preflight_contract",
        "validate_post_bridge_caveats",
        "validate_actionability_revalidation",
        "validate_computed_evidence_provenance",
        "validate_negative_evidence_handling",
        "validate_duplicate_schema_and_matrix",
        "validate_authorization_flags",
        "validate_forbidden_claims_and_actions",
        "validate_computed_verdict_source",
    }
    assert expected.issubset(observed)
    assert evaluation["all_gates_passed"] is True
    for row in observed.values():
        assert row["producer_function"] == row["validator"]
        assert row["code_path_hash"]
        assert row["aggregation_rule"]
        assert row["passed"] is True
        assert row["failures"] == []


def test_post_bridge_001d_caveats_claim_ceiling_and_authorization_remain_binding():
    runner = _runner()
    post_bridge = _read_json(ARTIFACT_DIR / "post_bridge_caveat_revalidation.json")

    assert post_bridge["artifact_path"] == "artifacts/post_bridge_admission_executable_001d/result.json"
    assert post_bridge["commit"] == runner.POST_BRIDGE_001D_COMMIT
    assert post_bridge["verdict"] == "post_bridge_admission_executable_001d_pass"
    assert post_bridge["bounded_pass"] is True
    assert post_bridge["claim_ceiling"]
    assert post_bridge["caveats_binding"] is True
    assert len(post_bridge["caveats"]) >= 3
    assert post_bridge["treat_as_mechanism_proof"] is False
    assert post_bridge["runtime_authorized"] is False
    assert post_bridge["bridge_ready_claim_allowed"] is False
    assert post_bridge["ego_ready_claim_allowed"] is False


def test_actionability_computed_evidence_negative_and_duplicate_guards_are_bounded():
    actionability = _read_json(ARTIFACT_DIR / "actionability_revalidation.json")
    computed = _read_json(ARTIFACT_DIR / "computed_evidence_provenance.json")
    negative = _read_json(ARTIFACT_DIR / "negative_evidence_handling.json")
    forbidden = _read_json(ARTIFACT_DIR / "forbidden_claims_and_actions.json")

    assert actionability["actionability_revalidation_passed"] is True
    assert actionability["all_required_rows_revalidated"] is True
    assert all(row["required"] is True and row["satisfied"] is True for row in actionability["revalidation_rows"])

    assert computed["computed_evidence_provenance_passed"] is True
    assert computed["static_or_literal_verdicts_allowed"] is False
    assert computed["all_required_outputs_have_callable_provenance"] is True
    for row in computed["artifact_provenance_rows"]:
        assert row["producer_function"]
        assert row["input_artifacts"]
        assert row["input_commits_tags_refs"]
        assert row["run_id"]
        assert row["aggregation_rule"]
        assert row["code_path_hash"]

    assert negative["negative_evidence_non_positive"] is True
    statuses = {row["task_id"]: row for row in negative["negative_evidence_rows"]}
    assert statuses["POST-BRIDGE-ADMISSION-EXECUTABLE-001B"]["positive_evidence_allowed"] is False
    assert statuses["POST-BRIDGE-ADMISSION-EXECUTABLE-001C"]["positive_evidence_allowed"] is False
    assert statuses["POST-BRIDGE-ADMISSION-EXECUTABLE-001D"]["mechanism_proof_allowed"] is False

    assert forbidden["duplicate_admission_schema_created"] is False
    assert forbidden["copied_45_row_matrix_detected"] is False


def test_authorization_flags_final_verdict_and_claim_ceiling_are_not_upgraded():
    runner = _runner()
    auth = _read_json(ARTIFACT_DIR / "authorization_flags.json")
    result = _read_json(ARTIFACT_DIR / "result.json")

    assert set(auth["authorization_flags"]) == AUTHORIZATION_FLAGS
    assert auth["all_authorization_flags_false"] is True
    assert all(value is False for value in auth["authorization_flags"].values())
    assert result["verdict"] == runner.VERDICT_PASS
    assert result["verdict"] not in FORBIDDEN_VERDICTS
    assert result["claim_ceiling"] == runner.CLAIM_CEILING
    assert set(result["what_this_does_not_prove"]).issuperset(WHAT_THIS_DOES_NOT_PROVE)
    assert result["authorization_flags"] == auth["authorization_flags"]
    assert result["all_gates_passed"] is True
    assert result["stop_conditions_triggered"] == []


def test_ablation_report_covers_required_negative_controls_and_each_fails():
    ablation = _read_json(ARTIFACT_DIR / "ablation_report.json")
    controls = {row["mutation_id"]: row for row in ablation["controls"]}

    assert set(controls) == set(NEGATIVE_CONTROLS)
    assert ablation["all_negative_controls_failed"] is True
    for mutation_id, expected_validator in NEGATIVE_CONTROLS.items():
        row = controls[mutation_id]
        assert row["expected_validator"] == expected_validator
        assert row["validation_failed"] is True
        assert expected_validator in row["failing_validators"]
        assert row["producer_function"] == "run_ablation_controls"


def test_admission_decision_trace_replays_result_json_verdict():
    runner = _runner()
    trace = _read_json(ARTIFACT_DIR / "admission_decision_trace.json")
    result = _read_json(ARTIFACT_DIR / "result.json")

    replayed = runner.replay_admission_verdict(trace["serialized_input_state"])

    assert trace["final_aggregation_trace"]["verdict"] == result["verdict"]
    assert replayed["verdict"] == result["verdict"]
    assert replayed["all_gates_passed"] == result["all_gates_passed"]
    assert replayed["stop_conditions_triggered"] == result["stop_conditions_triggered"]
    assert trace["replay_result_matches_result_json"] is True


def test_generated_artifacts_do_not_contain_copied_45_row_matrix():
    for name in REQUIRED_ARTIFACTS - {"claim_ceiling.txt"}:
        payload = _read_json(ARTIFACT_DIR / name)
        for path, value in _walk(payload):
            assert not (
                isinstance(value, list)
                and len(value) == 45
                and all(isinstance(item, dict) and "candidate_id" in item for item in value)
            ), f"copied 45-row matrix detected at {name}:{path}"


def test_callable_validators_reject_mutated_serialized_inputs():
    runner = _runner()
    state = runner.build_admission_state(repo_root=ROOT, output_dir=ARTIFACT_DIR, verify_remote=False)
    clean = runner.validate_admission_state(state)
    assert all(row["passed"] for row in clean)

    mutated = copy.deepcopy(state)
    mutated["parent_boundary_readback"]["parent_boundaries_by_id"]["preflight_001a"]["remote_resolved_commit"] = None
    failed = runner.validate_admission_state(mutated)
    assert any(row["validator"] == "validate_parent_boundaries" and not row["passed"] for row in failed)

    mutated = copy.deepcopy(state)
    mutated["post_bridge_caveat_revalidation"]["caveats"] = []
    failed = runner.validate_admission_state(mutated)
    assert any(row["validator"] == "validate_post_bridge_caveats" and not row["passed"] for row in failed)

    mutated = copy.deepcopy(state)
    mutated["authorization_flags"]["authorization_flags"]["authorize_ego_runtime"] = True
    failed = runner.validate_admission_state(mutated)
    assert any(row["validator"] == "validate_authorization_flags" and not row["passed"] for row in failed)

    mutated = copy.deepcopy(state)
    mutated["callable_gate_logic_executed"] = False
    mutated["static_pass_result"] = True
    failed = runner.validate_admission_state(mutated)
    assert any(row["validator"] == "validate_computed_verdict_source" and not row["passed"] for row in failed)

    mutated = copy.deepcopy(state)
    mutated["forbidden_claims_and_actions"]["inserted_claims"].append("Gate4 authorized")
    failed = runner.validate_admission_state(mutated)
    assert any(row["validator"] == "validate_forbidden_claims_and_actions" and not row["passed"] for row in failed)


def test_temp_run_uses_same_callable_logic_without_remote_dependency(tmp_path):
    runner = _runner()
    out = tmp_path / "admission"

    result = runner.run_admission_execution(repo_root=ROOT, output_dir=out, verify_remote=False)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in out.iterdir()})
    assert result["verdict"] == runner.VERDICT_PASS
    assert result["all_gates_passed"] is True
    assert _read_json(out / "parent_boundary_readback.json")["all_required_boundaries_resolved"] is True
    assert _read_json(out / "admission_decision_trace.json")["replay_result_matches_result_json"] is True


def test_protected_sealed_artifacts_were_not_modified():
    runner = _runner()
    result = _read_json(ARTIFACT_DIR / "result.json")

    assert result["protected_sealed_artifacts_modified"] is False
    assert result["protected_sealed_hashes_before"] == result["protected_sealed_hashes_after"]
    assert runner.hash_protected_inputs(ROOT) == result["protected_sealed_hashes_after"]
