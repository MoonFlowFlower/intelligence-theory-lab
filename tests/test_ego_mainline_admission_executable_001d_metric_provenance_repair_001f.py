import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TASK_ID = "EGO-MAINLINE-ADMISSION-EXECUTABLE-001D-METRIC-PROVENANCE-REPAIR-001F"
VERDICT_PASS = "ego_mainline_admission_executable_001d_metric_provenance_repair_001f_pass"
ARTIFACT_DIR = (
    ROOT
    / "artifacts"
    / "ego_mainline_admission_executable_001d_metric_provenance_repair_001f"
)
CLAIM_CEILING = (
    "bounded metric-provenance repair evidence for 001D under synthetic / controlled conditions only"
)

REQUIRED_ARTIFACTS = {
    "result.json",
    "parent_anchor_verification.json",
    "repair_scope_manifest.json",
    "001e_blocker_preservation_report.json",
    "metric_schema_repair_report.json",
    "context_consumption_report.json",
    "context_consumption_crosscheck.json",
    "metric_provenance.json",
    "metric_provenance_completeness_report.json",
    "old_artifact_inventory_before.json",
    "old_artifact_hashes_before.json",
    "old_artifact_hashes_after.json",
    "old_artifact_mutation_report.json",
    "old_artifact_mutation_provenance_report.json",
    "baseline_revalidation_report.json",
    "failure_path_context_consumption_report.json",
    "failure_path_old_artifact_mutation_provenance_report.json",
    "ablation_revalidation_report.json",
    "leakage_revalidation_report.json",
    "manual_injection_revalidation_report.json",
    "metadata_whitelist_scope_revalidation.json",
    "behavior_causal_replay_report.json",
    "frozen_input_consumption_report.json",
    "negative_evidence_preservation_report.json",
    "scope_leak_report.json",
    "claim_ceiling.txt",
}

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


def _module():
    return importlib.import_module(
        "ego_mainline_admission_executable_001d_metric_provenance_repair_001f.runner"
    )


def _core():
    return importlib.import_module(
        "ego_mainline_admission_executable_001d_metric_provenance_repair_001f.core"
    )


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _hash_tree(path: Path) -> dict[str, str]:
    hashes = {}
    for file in sorted(path.rglob("*")):
        if file.is_file():
            hashes[str(file.relative_to(path)).replace("\\", "/")] = hashlib.sha256(
                file.read_bytes()
            ).hexdigest()
    return hashes


def test_metric_provenance_repair_generates_required_artifacts_and_pass_result(tmp_path):
    runner = _module()
    out = tmp_path / "repair"

    result = runner.run_repair(repo_root=ROOT, output_dir=out, verify_remote=False)
    metrics = _read_json(out / "metric_provenance.json")
    completeness = _read_json(out / "metric_provenance_completeness_report.json")
    context = _read_json(out / "context_consumption_report.json")
    crosscheck = _read_json(out / "context_consumption_crosscheck.json")

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in out.iterdir()})
    assert result["task_id"] == TASK_ID
    assert result["verdict"] == VERDICT_PASS
    assert result["bounded_pass"] is True
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert result["acceptance_gates"]["all_verdict_metrics_have_callable_provenance"] is True
    assert completeness["all_verdict_metrics_have_callable_provenance"] is True
    assert completeness["all_verdict_metrics_have_train_context_ids_consumed"] is True
    assert completeness["all_verdict_metrics_have_heldout_context_ids_consumed"] is True
    assert completeness["all_verdict_metrics_have_counterfactual_pair_ids_consumed"] is True
    assert completeness["old_artifact_mutation_true_producer_provenance"] is True
    assert crosscheck["context_consumption_crosschecked_against_freeze"] is True
    assert context["context_consumption_fields_computed_by_callable_producers"] is True
    assert len(metrics["metrics"]) == 12
    for row in metrics["metrics"]:
        assert REQUIRED_METRIC_FIELDS.issubset(row)
        assert row["train_context_ids_consumed"]
        assert row["heldout_context_ids_consumed"]
        assert row["counterfactual_pair_ids_consumed"]
        assert row["computed_not_literal"] is True
        assert row["failure_path_available"] is True


def test_context_consumption_is_callable_crosschecked_and_not_decorative(tmp_path):
    runner = _module()
    out = tmp_path / "repair"

    runner.run_repair(repo_root=ROOT, output_dir=out, verify_remote=False)
    metrics = _read_json(out / "metric_provenance.json")
    context = _read_json(out / "context_consumption_report.json")
    crosscheck = _read_json(out / "context_consumption_crosscheck.json")
    frozen = _read_json(out / "frozen_input_consumption_report.json")

    context_ids_by_family = {
        family: {row["context_id"] for row in context["context_consumption_rows"] if row["context_family"] == family}
        for family in ["train", "heldout", "counterfactual_pair"]
    }
    frozen_families = frozen["families"]
    assert context_ids_by_family["train"] == set(frozen_families["train_context_ids"]["consumed"])
    assert context_ids_by_family["heldout"] == set(frozen_families["heldout_context_ids"]["consumed"])
    assert context_ids_by_family["counterfactual_pair"] == set(
        frozen_families["counterfactual_pair_ids"]["consumed"]
    )
    assert crosscheck["decorative_context_ids_detected"] == []

    for row in metrics["metrics"]:
        assert set(row["train_context_ids_consumed"]) <= context_ids_by_family["train"]
        assert set(row["heldout_context_ids_consumed"]) <= context_ids_by_family["heldout"]
        assert set(row["counterfactual_pair_ids_consumed"]) <= context_ids_by_family[
            "counterfactual_pair"
        ]
        assert all(
            context_row["producer_function"]
            for context_row in context["context_consumption_rows"]
            if row["metric_id"] in context_row["metric_ids_consuming_this_context"]
        )


def test_failure_paths_block_missing_empty_decorative_context_and_wrapper_provenance(tmp_path):
    core = _core()
    runner = _module()
    out = tmp_path / "repair"

    runner.run_repair(repo_root=ROOT, output_dir=out, verify_remote=False)
    metrics = _read_json(out / "metric_provenance.json")
    context = _read_json(out / "context_consumption_report.json")
    old_provenance = _read_json(out / "old_artifact_mutation_provenance_report.json")

    missing_train = json.loads(json.dumps(metrics))
    del missing_train["metrics"][0]["train_context_ids_consumed"]
    assert "train_context_ids_consumed_missing" in core.validate_metric_provenance(
        missing_train, context, old_provenance
    )["stop_conditions"]

    missing_heldout = json.loads(json.dumps(metrics))
    del missing_heldout["metrics"][0]["heldout_context_ids_consumed"]
    assert "heldout_context_ids_consumed_missing" in core.validate_metric_provenance(
        missing_heldout, context, old_provenance
    )["stop_conditions"]

    missing_counterfactual = json.loads(json.dumps(metrics))
    del missing_counterfactual["metrics"][0]["counterfactual_pair_ids_consumed"]
    assert "counterfactual_pair_ids_consumed_missing" in core.validate_metric_provenance(
        missing_counterfactual, context, old_provenance
    )["stop_conditions"]

    empty_contexts = json.loads(json.dumps(metrics))
    empty_contexts["metrics"][0]["train_context_ids_consumed"] = []
    assert "context_consumption_decorative" in core.validate_metric_provenance(
        empty_contexts, context, old_provenance
    )["stop_conditions"]

    decorative_contexts = json.loads(json.dumps(metrics))
    decorative_contexts["metrics"][0]["train_context_ids_consumed"] = ["decorative_train_ctx"]
    assert "context_consumption_decorative" in core.validate_metric_provenance(
        decorative_contexts, context, old_provenance
    )["stop_conditions"]

    wrapper_only = json.loads(json.dumps(metrics))
    for row in wrapper_only["metrics"]:
        if row["metric_id"] == "old_artifact_mutation":
            row["producer_function"] = (
                "ego_mainline_admission_executable_001d_metric_provenance_repair_001f.runner.run_repair"
            )
    assert "old_artifact_mutation_wrapper_only" in core.validate_metric_provenance(
        wrapper_only, context, old_provenance
    )["stop_conditions"]


def test_old_artifact_hashes_and_known_theory_file_boundary_are_enforced(tmp_path):
    core = _core()
    runner = _module()
    old_001d = ROOT / "artifacts" / "ego_mainline_admission_executable_001b_baseline_legal_input_repair_001d"
    old_001e = ROOT / "artifacts" / "ego_mainline_admission_executable_001d_independent_audit_001e"
    before = {"001d": _hash_tree(old_001d), "001e": _hash_tree(old_001e)}
    out = tmp_path / "repair"

    result = runner.run_repair(repo_root=ROOT, output_dir=out, verify_remote=False)
    mutation = _read_json(out / "old_artifact_mutation_report.json")
    provenance = _read_json(out / "old_artifact_mutation_provenance_report.json")
    scope = _read_json(out / "scope_leak_report.json")

    assert mutation["old_001d_artifacts_not_modified"] is True
    assert mutation["old_001e_artifacts_not_modified"] is True
    assert provenance["old_artifact_mutation_true_producer_provenance"] is True
    assert provenance["old_artifact_before_after_hashes_computed"] is True
    assert _hash_tree(old_001d) == before["001d"]
    assert _hash_tree(old_001e) == before["001e"]
    assert result["acceptance_gates"]["known_theory_file_left_unstaged_and_unmodified"] is True
    assert scope["known_theory_file_left_unstaged_and_unmodified"] is True

    missing_before = json.loads(json.dumps(provenance))
    missing_before["before_hashes_computed"] = False
    assert "old_artifact_hash_before_missing" in core.validate_old_artifact_mutation_provenance(
        missing_before
    )["stop_conditions"]

    missing_after = json.loads(json.dumps(provenance))
    missing_after["after_hashes_computed"] = False
    assert "old_artifact_hash_after_missing" in core.validate_old_artifact_mutation_provenance(
        missing_after
    )["stop_conditions"]


def test_materialized_artifact_dir_verifies_remote_anchors_and_git_boundary():
    runner = _module()

    result = runner.run_repair(repo_root=ROOT, output_dir=ARTIFACT_DIR, verify_remote=True)
    parents = _read_json(ARTIFACT_DIR / "parent_anchor_verification.json")

    assert REQUIRED_ARTIFACTS.issubset({path.name for path in ARTIFACT_DIR.iterdir()})
    assert result["verdict"] == VERDICT_PASS
    assert result["parent_anchors_verified"] is True
    assert all(row["local_verified"] and row["remote_verified"] for row in parents["anchors"])
    assert (ARTIFACT_DIR / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING

    cached = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    cached_paths = cached.stdout.splitlines()
    assert "docs/THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001A.md" not in cached_paths
    assert not any(
        path.startswith("docs/THEORY-LANDSCAPE-COVERAGE-COMPRESSION/")
        for path in cached_paths
    )
