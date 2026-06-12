import copy
import importlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TASK_ID = "EGO-MAINLINE-ADMISSION-EXECUTION-PREFLIGHT-001A"
ARTIFACT_DIR = ROOT / "artifacts" / "ego_mainline_admission_execution_preflight_001a"
DOC = ROOT / "docs" / "codex" / "tasks" / f"{TASK_ID}.md"

REQUIRED_ARTIFACTS = {
    "result.json",
    "parent_boundary_readback.json",
    "post_bridge_001d_readback.json",
    "alignment_contract_readback.json",
    "actionability_revalidation_preconditions.json",
    "computed_evidence_preconditions.json",
    "negative_evidence_preconditions.json",
    "forbidden_claims_and_actions.json",
    "authorization_flags.json",
    "claim_ceiling.txt",
}

FORBIDDEN_VERDICTS = {
    "EGO ready",
    "bridge ready",
    "runtime ready",
    "mechanism proven",
    "architecture valid",
    "Gate4 authorized",
    "companion authorized",
    "admission executed",
}

FORBIDDEN_CLAIMS = {
    "admission success",
    "EGO readiness",
    "bridge readiness",
    "runtime readiness",
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


def _runner():
    return importlib.import_module("ego_mainline_admission_execution_preflight_001a.runner")


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


def test_materialized_required_outputs_exist_parse_and_have_bounded_claim_ceiling():
    runner = _runner()

    assert DOC.exists()
    assert ARTIFACT_DIR.exists()
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})

    for name in REQUIRED_ARTIFACTS - {"claim_ceiling.txt"}:
        payload = _read_json(ARTIFACT_DIR / name)
        assert isinstance(payload, dict)
        meta = payload.get("computed_evidence_provenance")
        assert meta
        assert meta["producer_function"]
        assert meta["input_artifacts"]
        assert meta["input_refs_tags_commits"]
        assert meta["run_id"]
        assert meta["aggregation_rule"]
        assert meta["code_path_hash"]

    assert (ARTIFACT_DIR / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == runner.CLAIM_CEILING


def test_parent_boundaries_resolve_exactly_and_exclude_blocked_old_001a():
    runner = _runner()
    parents = _read_json(ARTIFACT_DIR / "parent_boundary_readback.json")
    rows = {row["boundary_id"]: row for row in parents["parent_boundaries"]}

    assert rows["alignment_001a"]["expected_commit"] == runner.ALIGNMENT_001A_COMMIT
    assert rows["alignment_001a"]["remote_tag"] == runner.ALIGNMENT_001A_TAG
    assert rows["alignment_001a"]["remote_resolved_commit"] == runner.ALIGNMENT_001A_COMMIT
    assert rows["alignment_001a"]["local_tag_resolved_commit"] == runner.ALIGNMENT_001A_COMMIT
    assert rows["alignment_001a"]["path_last_commit"] == runner.ALIGNMENT_001A_COMMIT

    assert rows["admission_coverage_reference_001a"]["remote_resolved_commit"] == runner.COVERAGE_REFERENCE_001A_COMMIT
    assert rows["canonicalization_provenance_repair_001b"]["remote_resolved_commit"] == runner.CANONICALIZATION_REPAIR_001B_COMMIT
    assert rows["coverage_compression_001d"]["remote_resolved_commit"] == runner.COVERAGE_COMPRESSION_001D_COMMIT
    assert rows["post_bridge_admission_executable_001d"]["path_last_commit"] == runner.POST_BRIDGE_001D_COMMIT
    assert rows["prior_readiness_audit_reference_only"]["path_last_commit"] == runner.PRIOR_READINESS_AUDIT_COMMIT

    assert parents["blocked_old_canonicalization_001a"]["commit"] == runner.BLOCKED_OLD_CANONICALIZATION_001A_COMMIT
    assert parents["blocked_old_canonicalization_001a"]["used_as_parent"] is False
    assert parents["all_required_boundaries_resolved"] is True


def test_post_bridge_001d_readback_preserves_verdict_caveats_and_claim_ceiling():
    runner = _runner()
    post_bridge = _read_json(ARTIFACT_DIR / "post_bridge_001d_readback.json")

    assert post_bridge["artifact_path"] == "artifacts/post_bridge_admission_executable_001d/result.json"
    assert post_bridge["commit"] == runner.POST_BRIDGE_001D_COMMIT
    assert post_bridge["verdict"] == "post_bridge_admission_executable_001d_pass"
    assert post_bridge["bounded_pass"] is True
    assert post_bridge["claim_ceiling"]
    assert len(post_bridge["caveats"]) >= 3
    assert post_bridge["treat_as_mechanism_proof"] is False
    assert post_bridge["runtime_authorized"] is False
    assert post_bridge["resolved"] is True


def test_alignment_contract_requires_actionability_computed_gate_and_negative_handling():
    alignment = _read_json(ARTIFACT_DIR / "alignment_contract_readback.json")
    actionability = _read_json(ARTIFACT_DIR / "actionability_revalidation_preconditions.json")
    computed = _read_json(ARTIFACT_DIR / "computed_evidence_preconditions.json")
    negative = _read_json(ARTIFACT_DIR / "negative_evidence_preconditions.json")

    assert alignment["resolved"] is True
    assert alignment["actionability_revalidation_required"] is True
    assert alignment["computed_evidence_gate_required_for_future_execution"] is True
    assert alignment["static_or_literal_verdicts_allowed"] is False
    assert alignment["negative_evidence_handling_required"] is True
    assert alignment["schema_duplication_allowed"] is False
    assert alignment["copied_45_row_matrix_detected"] is False
    assert alignment["post_bridge_001d_mechanism_proof_allowed"] is False

    assert actionability["all_preconditions_required"] is True
    assert all(row["required"] is True for row in actionability["preconditions"])

    assert computed["computed_evidence_gate_required_for_future_execution"] is True
    assert computed["static_or_literal_verdicts_allowed"] is False
    assert {"producer_function", "input_artifacts", "run_id", "aggregation_rule", "code_path_hash"}.issubset(
        computed["required_metadata_fields"]
    )

    statuses = {row["task_id"]: row for row in negative["negative_evidence_rows"]}
    assert statuses["POST-BRIDGE-ADMISSION-EXECUTABLE-001B"]["positive_evidence_allowed"] is False
    assert statuses["POST-BRIDGE-ADMISSION-EXECUTABLE-001C"]["positive_evidence_allowed"] is False
    assert statuses["POST-BRIDGE-ADMISSION-EXECUTABLE-001D"]["mechanism_proof_allowed"] is False


def test_authorization_flags_and_forbidden_claims_block_runtime_language():
    auth = _read_json(ARTIFACT_DIR / "authorization_flags.json")
    forbidden = _read_json(ARTIFACT_DIR / "forbidden_claims_and_actions.json")
    result = _read_json(ARTIFACT_DIR / "result.json")

    assert auth["all_authorization_flags_false"] is True
    assert auth["authorization_flags"]
    assert all(value is False for value in auth["authorization_flags"].values())
    assert auth["generated_from_resolved_state"] is True

    assert set(forbidden["forbidden_claims"]).issuperset(FORBIDDEN_CLAIMS)
    assert "admission execution" in forbidden["forbidden_actions"]
    assert "runtime authorization" in forbidden["forbidden_actions"]
    assert "Gate4 execution" in forbidden["forbidden_actions"]

    assert result["verdict"] == "pass_admission_execution_may_be_tasked_separately"
    assert result["verdict"] not in FORBIDDEN_VERDICTS
    assert set(result["what_this_does_not_prove"]).issuperset(FORBIDDEN_CLAIMS)
    assert all(value is False for value in result["authorization_flags"].values())


def test_result_is_callable_aggregated_and_negative_controls_cover_required_ablations():
    runner = _runner()
    result = _read_json(ARTIFACT_DIR / "result.json")

    assert result["producer_function"] == "build_result"
    assert result["callable_gate_logic_executed"] is True
    assert result["all_gates_passed"] is True
    assert result["stop_conditions_triggered"] == []
    assert result["protected_parent_artifacts_modified"] is False
    assert result["protected_parent_hashes_before"] == result["protected_parent_hashes_after"]
    assert result["duplicate_admission_schema_created"] is False
    assert result["copied_45_row_matrix_detected"] is False

    controls = {row["mutation_id"]: row for row in result["negative_controls"]["controls"]}
    expected = {
        "missing_alignment_001a_anchor",
        "missing_post_bridge_001d_verdict_caveat_claim_ceiling",
        "blocked_old_canonicalization_001a_used_as_parent",
        "authorization_flag_true",
        "static_pass_without_callable_gate_logic",
        "copied_45_row_matrix_or_duplicate_schema",
        "negative_001b_001c_treated_as_positive_downstream_evidence",
    }
    assert set(controls) == expected
    assert result["negative_controls"]["all_negative_controls_failed"] is True
    for row in controls.values():
        assert row["validation_failed"] is True
        assert row["failing_validators"]

    current_hashes = runner.hash_protected_inputs(ROOT)
    assert current_hashes == result["protected_parent_hashes_after"]


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
    state = runner.build_preflight_state(repo_root=ROOT, output_dir=ARTIFACT_DIR, verify_remote=False)
    clean = runner.validate_preflight_state(state)
    assert all(row["passed"] for row in clean)

    mutated = copy.deepcopy(state)
    mutated["parent_boundary_readback"]["parent_boundaries_by_id"]["alignment_001a"]["remote_resolved_commit"] = None
    failed = runner.validate_preflight_state(mutated)
    assert any(row["validator"] == "validate_parent_boundaries" and not row["passed"] for row in failed)

    mutated = copy.deepcopy(state)
    mutated["post_bridge_001d_readback"]["claim_ceiling"] = ""
    failed = runner.validate_preflight_state(mutated)
    assert any(row["validator"] == "validate_post_bridge_001d_readback" and not row["passed"] for row in failed)

    mutated = copy.deepcopy(state)
    mutated["authorization_flags"]["authorization_flags"]["runtime_authorized"] = True
    failed = runner.validate_preflight_state(mutated)
    assert any(row["validator"] == "validate_authorization_flags" and not row["passed"] for row in failed)


def test_temp_run_replays_same_callable_gate_without_remote_dependency(tmp_path):
    runner = _runner()
    out = tmp_path / "preflight"

    result = runner.run_preflight(repo_root=ROOT, output_dir=out, verify_remote=False)

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in out.iterdir()})
    assert result["verdict"] == "pass_admission_execution_may_be_tasked_separately"
    assert result["all_gates_passed"] is True
    assert result["negative_controls"]["all_negative_controls_failed"] is True
    assert _read_json(out / "parent_boundary_readback.json")["all_required_boundaries_resolved"] is True


def test_materialized_remote_anchor_and_git_scope_checks_are_callable():
    runner = _runner()
    result = runner.run_preflight(repo_root=ROOT, output_dir=ARTIFACT_DIR, verify_remote=True)
    parents = _read_json(ARTIFACT_DIR / "parent_boundary_readback.json")

    assert result["verdict"] == "pass_admission_execution_may_be_tasked_separately"
    assert parents["parent_boundaries_by_id"]["alignment_001a"]["remote_resolved_commit"] == runner.ALIGNMENT_001A_COMMIT
    assert parents["all_required_remote_anchors_verified"] is True

    changed = subprocess.run(
        ["git", "diff", "--name-only"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    changed_paths = set(changed.stdout.splitlines())
    protected = set(runner.PROTECTED_INPUTS_AS_POSIX)
    assert changed_paths.isdisjoint(protected)
