import hashlib
import importlib
import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


TASK_ID = "POST-BRIDGE-ADMISSION-EXECUTABLE-001D"
VERDICT = "post_bridge_admission_executable_001d_pass"
CLAIM_CEILING = (
    "bounded post-bridge admission evidence under computed-evidence provenance "
    "contract after leakage-gate repair only"
)
ARTIFACT_DIR = ROOT / "artifacts" / "post_bridge_admission_executable_001d"
CONTRACT_PATH = ROOT / "docs" / "codex" / "contracts" / "COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A.md"
TASK_CARD = ROOT / "docs" / "codex" / "tasks" / "POST-BRIDGE-ADMISSION-EXECUTABLE-001D.md"


REQUIRED_ARTIFACTS = {
    "stage0_freeze_manifest.json",
    "execution_manifest.json",
    "execution_manifest.sha256",
    "run_ledger.jsonl",
    "distribution_manifest.json",
    "serialized_state_provenance.jsonl",
    "metric_provenance.jsonl",
    "baseline_invocation_log.jsonl",
    "ablation_invocation_log.jsonl",
    "leakage_scanner_invocation_log.jsonl",
    "leakage_surface_inventory.json",
    "leakage_positive_control_report.json",
    "leakage_clean_control_report.json",
    "contrast_pair_consumption_log.jsonl",
    "frozen_input_consumption_report.json",
    "trace.jsonl",
    "candidate_input_rows.jsonl",
    "observation_seed_manifest.json",
    "serialized_state_snapshots.jsonl",
    "candidate_action_replay_report.json",
    "behavior_causal_replay_report.json",
    "trace_hash_replay_report.json",
    "state_hash_replay_report.json",
    "baseline_comparison.json",
    "ablation_report.json",
    "contrast_report.json",
    "leakage_report.json",
    "mutation_check_report.json",
    "protected_artifact_inventory_before.json",
    "protected_artifact_hashes_before.json",
    "protected_artifact_hashes_after.json",
    "tracked_old_artifact_mutation_report.json",
    "computed_evidence_provenance_report.json",
    "result.json",
    "claim_ceiling.txt",
}

REQUIRED_SURFACES = {
    "candidate_inputs",
    "trace_rows",
    "serialized_state_snapshots",
    "observation_rows",
    "serialized_state_provenance",
    "metric_provenance_rows",
    "artifact_paths",
    "fixture_names",
    "labels",
    "verifier_only_fields",
    "future_observations",
    "future_partner_responses",
    "later_action_labels",
    "post_hoc_metrics",
    "test_only_schema_paths",
}


def _modules():
    core = importlib.import_module("post_bridge_admission_executable_001d.core")
    runner = importlib.import_module("post_bridge_admission_executable_001d.runner")
    return core, runner


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def run_001d(tmp_path_factory):
    core, runner = _modules()
    out = tmp_path_factory.mktemp("post_bridge_admission_001d")
    result = runner.run_admission_001d(
        repo_root=ROOT,
        output_dir=out,
        enforce_clean_worktree=False,
    )
    return core, out, result


def test_001d_run_emits_required_artifacts_and_cites_contract(run_001d):
    core, out, result = run_001d

    assert result["task_id"] == TASK_ID
    assert result["verdict"] == VERDICT
    assert result["bounded_pass"] is True
    assert result["artifact_dir"] == "artifacts/post_bridge_admission_executable_001d"
    assert result["claim_ceiling"] == CLAIM_CEILING
    assert REQUIRED_ARTIFACTS.issubset({path.name for path in out.iterdir()})
    assert not (out / "failure_manifest.json").exists()
    assert (out / "claim_ceiling.txt").read_text(encoding="utf-8").strip() == CLAIM_CEILING
    assert core.CONTRACT_PATH == "docs/codex/contracts/COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A.md"
    assert "COMPUTED-EVIDENCE-PROVENANCE-CONTRACT-001A" in TASK_CARD.read_text(encoding="utf-8")


def test_stage0_freeze_covers_remote_anchors_contract_agents_and_registries(run_001d):
    core, out, _result = run_001d
    stage0 = _read_json(out / "stage0_freeze_manifest.json")
    distribution = _read_json(out / "distribution_manifest.json")
    manifest = _read_json(out / "execution_manifest.json")

    assert stage0["stage0_freeze_before_any_executable_run"] is True
    assert stage0["executable_run_started_before_stage0"] is False
    assert stage0["canonical_clean_worktree_required"] is True
    assert stage0["clean_worktree_before_stage0"]["enforced"] is False
    assert stage0["parent_remote_anchor_verification"]["verified"] is True
    assert all("git ls-remote origin refs/tags/" in command for command in stage0["parent_remote_anchor_verification"]["commands"])
    assert stage0["computed_evidence_contract"]["path"] == core.CONTRACT_PATH
    assert stage0["computed_evidence_contract"]["hash"] == _file_sha(CONTRACT_PATH)
    assert stage0["agents_instruction_hash"] == _file_sha(ROOT / "AGENTS.md")
    assert set(stage0["baseline_implementation_registry"]) == set(core.REQUIRED_BASELINES)
    assert set(stage0["ablation_intervention_registry"]) == set(core.REQUIRED_ABLATIONS)
    assert set(stage0["leakage_scanner_registry"]) == set(core.REQUIRED_LEAKAGE_SCANNERS)
    assert set(stage0["leakage_scanner_registry"]) == REQUIRED_SURFACES
    assert _file_sha(out / "execution_manifest.json") == (out / "execution_manifest.sha256").read_text(encoding="utf-8").strip()
    assert manifest["stage0_freeze_manifest_hash"] == _file_sha(out / "stage0_freeze_manifest.json")

    assert distribution["actual_counts"]["train_contexts"] >= 24
    assert distribution["actual_counts"]["heldout_bridge_contexts"] >= 48
    assert distribution["actual_counts"]["counterfactual_state_pairs"] >= 16
    assert distribution["actual_counts"]["cross_agent_state_swap_pairs"] >= 16
    assert distribution["actual_counts"]["duplicate_identity_token_contrasts"] >= 16
    assert distribution["actual_counts"]["independent_seed_families"] >= 4


def test_leakage_scanners_scan_full_real_surfaces_and_same_surface_controls(run_001d):
    core, out, _result = run_001d
    report = _read_json(out / "leakage_report.json")
    inventory = _read_json(out / "leakage_surface_inventory.json")
    log = _read_jsonl(out / "leakage_scanner_invocation_log.jsonl")

    inventory_by_name = {row["scanner_name"]: row for row in inventory["surfaces"]}
    assert set(core.REQUIRED_LEAKAGE_SCANNERS) == {row["scanner_name"] for row in log}
    assert set(inventory_by_name) == set(core.REQUIRED_LEAKAGE_SCANNERS)
    assert report["leakage_gate_passed"] is True
    assert report["addresses_001c_redteam_leakage_blocker"] is True

    for row in log:
        surface = inventory_by_name[row["scanner_name"]]
        assert row["scanned_surface_id"] == surface["scanned_surface_id"]
        assert row["scanned_surface_type"] == surface["scanned_surface_type"]
        assert row["full_surface_scanned"] is True
        assert row["sanitized_projection_scan"] is False
        assert row["constant_dictionary_scan"] is False
        assert row["positive_control"]["same_surface_class"] is True
        assert row["positive_control"]["detected"] is True
        assert row["clean_control"]["same_surface_class"] is True
        assert row["clean_control"]["detected"] is False
        assert row["real_scan"]["detected"] is False
        assert row["positive_control_surface_id"] != row["clean_control_surface_id"]
        assert row["scanner_function"].endswith("leakage_scan_surface")
        assert len(row["code_path_hash"]) == 64


def test_positive_and_clean_control_reports_are_same_surface_class(run_001d):
    _core, out, _result = run_001d
    positives = _read_json(out / "leakage_positive_control_report.json")
    cleans = _read_json(out / "leakage_clean_control_report.json")

    assert positives["all_positive_controls_detected"] is True
    assert cleans["all_clean_controls_clean"] is True
    assert {row["scanner_name"] for row in positives["controls"]} == REQUIRED_SURFACES
    assert {row["scanner_name"] for row in cleans["controls"]} == REQUIRED_SURFACES
    assert all(row["same_surface_class"] for row in positives["controls"])
    assert all(row["same_surface_class"] for row in cleans["controls"])
    assert all(row["injected_forbidden_token"] for row in positives["controls"])


def test_leakage_metric_provenance_identifies_scanned_surface_ids(run_001d):
    _core, out, _result = run_001d
    metric_rows = _read_jsonl(out / "metric_provenance.jsonl")
    log = _read_jsonl(out / "leakage_scanner_invocation_log.jsonl")
    log_by_name = {row["scanner_name"]: row for row in log}
    leakage_rows = [row for row in metric_rows if row["metric_id"].startswith("leakage::")]

    assert {row["metric_id"].split("::", 1)[1] for row in leakage_rows} == REQUIRED_SURFACES
    for row in leakage_rows:
        scanner_name = row["metric_id"].split("::", 1)[1]
        invocation = log_by_name[scanner_name]
        assert row["scanned_surface_ids"] == [invocation["scanned_surface_id"]]
        assert row["positive_control_surface_ids"] == [invocation["positive_control_surface_id"]]
        assert row["clean_control_surface_ids"] == [invocation["clean_control_surface_id"]]
        assert row["input_surface_ids"] == [
            invocation["scanned_surface_id"],
            invocation["positive_control_surface_id"],
            invocation["clean_control_surface_id"],
        ]
        assert row["input_artifact_paths"]
        assert set(row["input_artifact_paths"]) == set(row["input_artifact_hashes"])


def test_forbidden_source_scan_result_is_computed_not_constant(run_001d):
    _core, out, _result = run_001d
    rows = _read_jsonl(out / "serialized_state_provenance.jsonl")

    assert rows
    for row in rows:
        scan = row["forbidden_source_scan_result"]
        assert scan["computed_not_literal"] is True
        assert scan["scanner_function"].endswith("leakage_scan_surface")
        assert scan["scanned_surface_id"].startswith("serialized_state_provenance_source:")
        assert len(scan["code_path_hash"]) == 64
        assert "clean" in scan and "hits" in scan
        assert set(scan) != {"clean", "hits"}


def test_candidate_score_is_derived_from_replay_not_literal(run_001d):
    _core, out, _result = run_001d
    baseline = _read_json(out / "baseline_comparison.json")
    ablation = _read_json(out / "ablation_report.json")
    replay = _read_json(out / "candidate_action_replay_report.json")
    metrics = _read_jsonl(out / "metric_provenance.jsonl")
    candidate_metric = next(row for row in metrics if row["metric_id"] == "candidate_score")

    assert baseline["candidate"]["candidate_score"] == replay["candidate_score"]
    assert baseline["candidate"]["score_source"] == "computed_from_behavior_causal_replay_outputs"
    assert baseline["candidate"]["candidate_score_computed_not_literal"] is True
    assert ablation["candidate_score"] == replay["candidate_score"]
    assert ablation["candidate_score_source"] == "computed_from_behavior_causal_replay_outputs"
    assert candidate_metric["producer_function"] == replay["replay_function"]
    assert candidate_metric["computed_not_literal"] is True


def test_replay_baseline_ablation_frozen_inputs_and_mutation_protections_remain(run_001d):
    core, out, result = run_001d
    baseline = _read_json(out / "baseline_comparison.json")
    ablation = _read_json(out / "ablation_report.json")
    behavior = _read_json(out / "behavior_causal_replay_report.json")
    candidate = _read_json(out / "candidate_action_replay_report.json")
    consumption = _read_json(out / "frozen_input_consumption_report.json")
    mutation = _read_json(out / "tracked_old_artifact_mutation_report.json")
    baseline_log = _read_jsonl(out / "baseline_invocation_log.jsonl")
    ablation_log = _read_jsonl(out / "ablation_invocation_log.jsonl")

    assert set(core.REQUIRED_BASELINES) == {row["baseline_name"] for row in baseline_log}
    assert all(row["computed_from_outputs"] for row in baseline_log)
    assert baseline["baseline_gate_passed"] is True
    assert set(core.REQUIRED_ABLATIONS) == {row["ablation_name"] for row in ablation_log}
    assert all(row["reran_candidate_behavior"] for row in ablation_log)
    assert ablation["ablation_gate_passed"] is True
    assert behavior["behavior_causal_replay_passed"] is True
    assert behavior["hash_only_replay"] is False
    assert candidate["candidate_action_replay_passed"] is True
    assert consumption["unused_frozen_inputs"] == []
    assert mutation["old_artifact_mutation_detected"] is False
    assert result["acceptance_gates"]["trace_hash_replay_hygiene_only"] is True
    assert result["acceptance_gates"]["state_hash_replay_hygiene_only"] is True


def test_failure_paths_emit_specific_001d_blocker_verdicts():
    core, _runner = _modules()
    metric_fields = {
        "metric_id": "leakage::candidate_inputs",
        "metric_name": "leakage scanner result",
        "producer_function": "fn",
        "producer_module": "post_bridge_admission_executable_001d.core",
        "code_path_hash": "0" * 64,
        "run_id": core.RUN_ID,
        "episode_ids": ["episode_000"],
        "seed_ids": ["seed_family_0"],
        "train_context_ids_consumed": ["train_context_000"],
        "heldout_context_ids_consumed": ["heldout_context_000"],
        "counterfactual_pair_ids_consumed": [],
        "input_artifact_paths": ["trace.jsonl"],
        "input_artifact_hashes": {"trace.jsonl": "1" * 64},
        "input_row_count": 1,
        "output_artifact_path": "leakage_report.json",
        "output_row_ids": ["candidate_inputs"],
        "aggregation_rule": "positive control detects, clean control and real scan do not detect",
        "threshold_used": "positive control required and real scan clean",
        "threshold_frozen_before_run": True,
        "computed_not_literal": True,
        "failure_path_available": True,
    }
    baseline_invocations = [
        {"baseline_name": name, "invoked": True, "computed_from_outputs": True}
        for name in core.REQUIRED_BASELINES
    ]
    ablation_invocations = [
        {"ablation_name": name, "invoked": True, "reran_candidate_behavior": True}
        for name in core.REQUIRED_ABLATIONS
    ]
    good_leakage = [
        {
            "scanner_name": name,
            "positive_control": {"detected": True, "same_surface_class": True},
            "clean_control": {"detected": False, "same_surface_class": True},
            "real_scan": {"detected": False},
            "full_surface_scanned": True,
            "sanitized_projection_scan": False,
            "constant_dictionary_scan": False,
            "scanned_surface_id": f"surface:{name}",
            "positive_control_surface_id": f"surface:{name}:positive",
            "clean_control_surface_id": f"surface:{name}:clean",
        }
        for name in core.REQUIRED_LEAKAGE_SCANNERS
    ]

    assert core.evaluate_computed_evidence_gate(
        metric_rows=[],
        baseline_invocations=[],
        ablation_invocations=[],
        leakage_invocations=[],
        replay_report={"behavior_causal_replay_passed": True, "hash_only_replay": False},
        consumption_report={"unused_frozen_inputs": []},
        serialized_state_provenance_rows=[],
    )["verdict"] == "post_bridge_admission_executable_001d_failed_computed_evidence_provenance"

    assert core.evaluate_computed_evidence_gate(
        metric_rows=[{**metric_fields, "metric_id": "candidate_score", "computed_not_literal": False}],
        baseline_invocations=baseline_invocations,
        ablation_invocations=ablation_invocations,
        leakage_invocations=good_leakage,
        replay_report={"behavior_causal_replay_passed": True, "hash_only_replay": False},
        consumption_report={"unused_frozen_inputs": []},
        serialized_state_provenance_rows=[],
    )["verdict"] == "post_bridge_admission_executable_001d_failed_candidate_score_literal"

    assert core.evaluate_computed_evidence_gate(
        metric_rows=[metric_fields],
        baseline_invocations=baseline_invocations,
        ablation_invocations=ablation_invocations,
        leakage_invocations=[{**row, "full_surface_scanned": False} for row in good_leakage],
        replay_report={"behavior_causal_replay_passed": True, "hash_only_replay": False},
        consumption_report={"unused_frozen_inputs": []},
        serialized_state_provenance_rows=[],
    )["verdict"] == "post_bridge_admission_executable_001d_failed_sanitized_surface_scan"

    assert core.evaluate_computed_evidence_gate(
        metric_rows=[{**metric_fields, "scanned_surface_ids": []}],
        baseline_invocations=baseline_invocations,
        ablation_invocations=ablation_invocations,
        leakage_invocations=good_leakage,
        replay_report={"behavior_causal_replay_passed": True, "hash_only_replay": False},
        consumption_report={"unused_frozen_inputs": []},
        serialized_state_provenance_rows=[],
    )["verdict"] == "post_bridge_admission_executable_001d_failed_missing_metric_provenance_surface_id"
