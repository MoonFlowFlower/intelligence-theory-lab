import hashlib
import inspect
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from evidence_admission_verifier_001a.core import (
    REQUIRED_OUTPUTS,
    verify_bundle,
    write_admission_artifacts,
)


TASK_CARD = ROOT / "docs" / "codex" / "tasks" / "EVIDENCE-ADMISSION-VERIFIER-001A.md"
CLAIM_CEILING = (
    "standalone evidence-admission filtering for future citation only; no Gate repair, "
    "no mechanism validity"
)
CALLABLE_AGGREGATION_RULE = "callable_result_digest_v1"
CALLABLE_RECOMPUTE_CONTRACT = "callable_result_digest_v1"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def callable_digest_metric(
    input_paths: list[Path],
    output_dir: Path,
    run_id: str,
    aggregation_rule: str,
) -> dict:
    input_hashes = {}
    total_bytes = 0
    for input_path in input_paths:
        raw = Path(input_path).read_bytes()
        input_hashes[Path(input_path).name] = hashlib.sha256(raw).hexdigest()
        total_bytes += len(raw)
    payload = {
        "aggregation_rule": aggregation_rule,
        "input_hashes": input_hashes,
        "run_id": run_id,
        "total_bytes": total_bytes,
    }
    digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_json(output_dir / "callable_digest_metric.json", {**payload, "output_digest": digest})
    return {
        "aggregation_rule": aggregation_rule,
        "metric_value": total_bytes,
        "output_digest": digest,
        "output_row_count": len(input_paths),
    }


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _source_hash_for(function) -> str:
    source_path = inspect.getsourcefile(function)
    assert source_path is not None
    return _sha256_file(Path(source_path))


def _producer_path(function) -> str:
    return f"{function.__module__}:{function.__name__}"


def _expected_callable_result(bundle: Path, run_id: str, aggregation_rule: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        return callable_digest_metric(
            input_paths=[bundle / "inputs" / "episodes.jsonl"],
            output_dir=Path(tmp),
            run_id=run_id,
            aggregation_rule=aggregation_rule,
        )


def _metric(metric_id: str, role: str, producer: str, bundle: Path) -> dict:
    run_id = f"run-clean-{metric_id}"
    expected = _expected_callable_result(bundle, run_id, CALLABLE_AGGREGATION_RULE)
    return {
        "metric_id": metric_id,
        "metric_name": metric_id.replace("_", " "),
        "evidence_role": role,
        "producer_function": producer,
        "producer_module": producer.split(":", 1)[0],
        "code_path_hash": "sha256:" + _source_hash_for(callable_digest_metric),
        "run_id": run_id,
        "episode_ids": ["episode-1"],
        "seed_ids": ["seed-1"],
        "train_context_ids_consumed": ["train-1"],
        "heldout_context_ids_consumed": ["heldout-1"],
        "counterfactual_pair_ids_consumed": ["pair-1"],
        "input_artifact_paths": ["inputs/episodes.jsonl"],
        "input_artifact_hashes": {
            "inputs/episodes.jsonl": "sha256:" + _sha256_file(bundle / "inputs" / "episodes.jsonl")
        },
        "input_row_count": 1,
        "output_artifact_path": f"outputs/{metric_id}.jsonl",
        "output_row_ids": [f"{metric_id}-row-1"],
        "aggregation_rule": CALLABLE_AGGREGATION_RULE,
        "threshold_used": 0.5,
        "threshold_frozen_before_run": True,
        "computed_not_literal": True,
        "failure_path_available": True,
        "recompute_contract": CALLABLE_RECOMPUTE_CONTRACT,
        "expected_metric_value": expected["metric_value"],
        "expected_output_digest": "sha256:" + expected["output_digest"],
        "expected_output_row_count": expected["output_row_count"],
    }


def _write_clean_bundle(bundle: Path) -> None:
    bundle.mkdir(parents=True, exist_ok=True)
    (bundle / "inputs").mkdir(parents=True, exist_ok=True)
    (bundle / "inputs" / "episodes.jsonl").write_text(
        json.dumps({"episode_id": "episode-1", "observation": "alpha"}, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    producer = _producer_path(callable_digest_metric)
    (bundle / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")
    (bundle / "report.md").write_text("bounded evidence report only\n", encoding="utf-8")
    _write_json(
        bundle / "result.json",
        {
            "verdict": "local_report_pass_string_ignored_by_verifier",
            "admitted_for_citation": True,
            "candidate_score": 1.0,
        },
    )
    _write_jsonl(
        bundle / "invocation_ledger.jsonl",
        [
            {
                "call_id": "call-candidate",
                "function_name": "candidate_score",
                "producer_function": producer,
                "called": True,
                "run_id": "run-clean-candidate_score",
                "input_artifacts": ["inputs/episodes.jsonl"],
                "output_artifact": "outputs/candidate_score.jsonl",
            },
            {
                "call_id": "call-baseline",
                "function_name": "count_table_baseline",
                "producer_function": producer,
                "called": True,
                "run_id": "run-clean-baseline_score",
                "input_artifacts": ["inputs/episodes.jsonl"],
                "output_artifact": "outputs/baseline_score.jsonl",
            },
            {
                "call_id": "call-ablation",
                "function_name": "remove_state_ablation",
                "producer_function": producer,
                "called": True,
                "run_id": "run-clean-ablation_score",
                "input_artifacts": ["inputs/episodes.jsonl"],
                "output_artifact": "outputs/ablation_score.jsonl",
            },
            {
                "call_id": "call-leakage",
                "function_name": "scan_forbidden_fields",
                "producer_function": producer,
                "called": True,
                "run_id": "run-clean-leakage_scan",
                "input_artifacts": ["inputs/episodes.jsonl"],
                "output_artifact": "outputs/leakage_scan.json",
            },
            {
                "call_id": "call-replay",
                "function_name": "recompute_behavior_replay",
                "producer_function": producer,
                "called": True,
                "run_id": "run-clean-behavior_replay",
                "input_artifacts": ["serialized/state.json", "inputs/observation.json"],
                "output_artifact": "outputs/replay.json",
            },
        ],
    )
    _write_jsonl(
        bundle / "metric_provenance.jsonl",
        [
            _metric("candidate_score", "candidate_metric", producer, bundle),
            _metric("baseline_score", "baseline_metric", producer, bundle),
            _metric("ablation_score", "ablation_metric", producer, bundle),
            _metric("leakage_scan", "leakage_metric", producer, bundle),
            _metric("behavior_replay", "replay_metric", producer, bundle),
        ],
    )
    _write_jsonl(
        bundle / "baseline_invocations.jsonl",
        [
            {
                "baseline_id": "count_table",
                "function_name": "count_table_baseline",
                "called": True,
                "independent_callable": True,
                "computed_not_literal": True,
                "input_row_ids": ["episode-1"],
                "output_row_ids": ["baseline-row-1"],
                "run_id": "run-clean",
            }
        ],
    )
    _write_jsonl(
        bundle / "ablation_invocations.jsonl",
        [
            {
                "ablation_id": "remove_state",
                "intervention_function": "remove_state_ablation",
                "called": True,
                "intervention_applied": True,
                "episodes_rerun": True,
                "score_recomputed": True,
                "pre_intervention_state_hashes": ["sha256:before"],
                "post_intervention_state_hashes": ["sha256:after"],
                "output_row_ids": ["ablation-row-1"],
                "run_id": "run-clean",
            }
        ],
    )
    _write_json(
        bundle / "leakage_scan_report.json",
        {
            "scanner_function": "scan_forbidden_fields",
            "called": True,
            "computed_not_literal": True,
            "scanned_surfaces": ["candidate_inputs", "trace", "serialized_state"],
            "positive_control_present": True,
            "positive_control_detected": True,
            "clean_control_passed": True,
        },
    )
    _write_json(
        bundle / "replay_recompute_report.json",
        {
            "replay_function": "recompute_behavior_replay",
            "called": True,
            "computed_not_literal": True,
            "behavior_recomputed": True,
            "used_serialized_state": True,
            "used_observation": True,
            "compared_action": True,
            "hash_only": False,
            "stored_actions_reused": False,
        },
    )
    _write_json(
        bundle / "frozen_input_consumption.json",
        {
            "required_input_ids": ["seed-1", "heldout-1", "pair-1"],
            "consumed_input_ids": ["seed-1", "heldout-1", "pair-1"],
            "unused_input_ids": [],
        },
    )


def _bundle(tmp_path: Path, name: str) -> Path:
    path = tmp_path / name
    _write_clean_bundle(path)
    return path


def _remove(path: Path) -> None:
    if path.exists():
        path.unlink()


def test_clean_minimal_bundle_admits_and_writes_recomputable_outputs(tmp_path):
    bundle = _bundle(tmp_path, "clean")
    out = tmp_path / "out"

    decision = verify_bundle(bundle, run_id="test-run-clean")
    write_admission_artifacts(decision, out)

    assert decision["canonical_decision"] == "admitted_for_citation"
    assert decision["decision_basis"] == "computed_bundle_evidence"
    assert decision["block_reason_ids"] == []
    assert REQUIRED_OUTPUTS == {path.name for path in out.iterdir()}

    result = json.loads((out / "result.json").read_text(encoding="utf-8"))
    admission = json.loads((out / "admission_decision.json").read_text(encoding="utf-8"))
    matrix = json.loads((out / "block_reason_matrix.json").read_text(encoding="utf-8"))
    verified_rows = [
        json.loads(line)
        for line in (out / "verified_provenance_rows.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert result["admission_decision"] == admission["canonical_decision"]
    assert admission["canonical_decision"] == "admitted_for_citation"
    assert matrix["blocking"] is False
    assert len(verified_rows) >= 5
    assert all(row["computed"] is True for row in verified_rows)
    assert admission["verdict_text_used"] is False
    assert admission["producer_function"] == "verify_bundle"
    assert admission["aggregation_rule"] == "first blocking evidence-admission rule in fixed precedence order"


def test_false_and_missing_evidence_fixtures_block_for_computed_reasons(tmp_path):
    cases = []

    fake = tmp_path / "fake_pass"
    fake.mkdir()
    _write_json(
        fake / "result.json",
        {"verdict": "bounded_pass", "admitted_for_citation": True, "candidate_score": 1.0},
    )
    (fake / "report.md").write_text("ready for downstream citation\n", encoding="utf-8")
    cases.append((fake, "blocked_fake_pass", "fake_pass_without_callable_provenance"))

    missing_baseline = _bundle(tmp_path, "missing_baseline")
    _remove(missing_baseline / "baseline_invocations.jsonl")
    cases.append((missing_baseline, "blocked_missing_baseline", "missing_callable_baseline_invocation"))

    missing_ablation = _bundle(tmp_path, "missing_ablation")
    _remove(missing_ablation / "ablation_invocations.jsonl")
    cases.append((missing_ablation, "blocked_missing_ablation_rerun", "missing_ablation_rerun"))

    missing_leakage_control = _bundle(tmp_path, "missing_leakage_control")
    _write_json(
        missing_leakage_control / "leakage_scan_report.json",
        {
            "scanner_function": "scan_forbidden_fields",
            "called": True,
            "computed_not_literal": True,
            "scanned_surfaces": ["candidate_inputs"],
            "positive_control_present": False,
            "positive_control_detected": False,
            "clean_control_passed": True,
        },
    )
    cases.append(
        (
            missing_leakage_control,
            "blocked_missing_leakage_positive_control",
            "missing_leakage_positive_control",
        )
    )

    hash_only_replay = _bundle(tmp_path, "hash_only_replay")
    _write_json(
        hash_only_replay / "replay_recompute_report.json",
        {
            "replay_function": "hash_replay",
            "called": True,
            "computed_not_literal": True,
            "behavior_recomputed": False,
            "used_serialized_state": False,
            "used_observation": False,
            "compared_action": False,
            "hash_only": True,
            "stored_actions_reused": True,
        },
    )
    cases.append((hash_only_replay, "blocked_missing_replay_recompute", "hash_only_replay"))

    for bundle, expected_decision, expected_reason in cases:
        decision = verify_bundle(bundle, run_id=f"test-run-{bundle.name}")
        assert decision["canonical_decision"] == expected_decision
        assert expected_reason in decision["block_reason_ids"]
        assert decision["decision_basis"] == "computed_bundle_evidence"
        assert decision["verdict_text_used"] is False
        assert decision["block_reason_matrix"]["blocking"] is True
        assert all(reason["computed"] is True for reason in decision["block_reason_matrix"]["reasons"])
        assert not any(reason["source"] == "result_or_report_verdict" for reason in decision["block_reason_matrix"]["reasons"])


def test_result_json_and_report_edits_cannot_admit_missing_callable_evidence(tmp_path):
    bundle = _bundle(tmp_path, "missing_baseline_with_claim_edits")
    _remove(bundle / "baseline_invocations.jsonl")

    before = verify_bundle(bundle, run_id="before-text-edit")
    _write_json(
        bundle / "result.json",
        {
            "verdict": "admitted_for_citation",
            "admitted_for_citation": True,
            "baseline_gate_passed": True,
            "candidate_score": 1.0,
        },
    )
    (bundle / "report.md").write_text(
        "This report says pass, ready, and admitted for citation.\n",
        encoding="utf-8",
    )
    after = verify_bundle(bundle, run_id="after-text-edit")

    assert before["canonical_decision"] == "blocked_missing_baseline"
    assert after["canonical_decision"] == "blocked_missing_baseline"
    assert before["block_reason_ids"] == after["block_reason_ids"]
    assert after["verdict_text_used"] is False


def test_claim_inflation_blocks_even_when_provenance_is_clean(tmp_path):
    bundle = _bundle(tmp_path, "inflated_claim")
    (bundle / "report.md").write_text(
        "This proves EGO readiness, mechanism validity, consciousness, and stable user benefit.\n",
        encoding="utf-8",
    )

    decision = verify_bundle(bundle, run_id="claim-inflation")

    assert decision["canonical_decision"] == "blocked_claim_inflation"
    assert "claim_inflation_detected" in decision["block_reason_ids"]
    assert decision["verdict_text_used"] is False


def test_cli_writes_required_outputs(tmp_path):
    bundle = _bundle(tmp_path, "clean_cli")
    out = tmp_path / "cli_out"
    env = {**os.environ, "PYTHONPATH": os.pathsep.join([str(ROOT / "src"), str(ROOT / "tests")])}

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "evidence_admission_verifier_001a",
            str(bundle),
            "--out",
            str(out),
            "--run-id",
            "cli-test-run",
        ],
        cwd=ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert REQUIRED_OUTPUTS == {path.name for path in out.iterdir()}
    admission = json.loads((out / "admission_decision.json").read_text(encoding="utf-8"))
    assert admission["canonical_decision"] == "admitted_for_citation"
    assert "admitted_for_citation" in completed.stdout


def test_task_card_preserves_scope_boundaries():
    text = TASK_CARD.read_text(encoding="utf-8")

    assert "Auto-Remote-Anchor: forbidden" in text
    assert "src/gate3_viability_functional_affect_001b/" in text
    assert "src/gate4_*" in text
    assert "src/ego_mainline_*" in text
    assert "Historical artifacts remain read-only evidence records." in text
    assert "This task does not authorize committing, pushing, tagging" in text
