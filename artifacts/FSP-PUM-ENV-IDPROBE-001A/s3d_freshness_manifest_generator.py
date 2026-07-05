"""Generate freshness/readback manifest for the S3d line-30 battery attempt.

This artifact-side generator is intentionally separate from the battery runner so
post-run verification command counts can be recorded without editing the frozen
science contract.  It does not adjudicate S3d; it only hashes emitted artifacts
and summarizes the already-emitted STOP result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "FSP-PUM-ENV-IDPROBE-001A"
ARTIFACT_ROOT = ROOT / "artifacts" / TASK_ID
OUT = ARTIFACT_ROOT / "s3d_freshness_manifest.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _artifact_ref(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "exists": path.exists(),
        "sha256": _sha256(path) if path.exists() else None,
        "size_bytes": path.stat().st_size if path.exists() else None,
    }


def _code_hash(paths: list[Path]) -> str:
    h = hashlib.sha256()
    for path in paths:
        h.update(str(path.relative_to(ROOT)).replace("\\", "/").encode("utf-8"))
        h.update(path.read_bytes())
    return h.hexdigest()


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, Path):
        return str(value)
    return value


def build_manifest(py_compile_files: int, pytest_passed: int, pytest_timeout_count: int) -> dict[str, Any]:
    result = _read_json(ARTIFACT_ROOT / "result.json")
    failure = _read_json(ARTIFACT_ROOT / "failure_manifest.json")
    certificate = _read_json(ARTIFACT_ROOT / "s3d_certificate_report.json")
    projection_path = ARTIFACT_ROOT / "s3d_compute_projection_line30.0.json"
    projection = _read_json(projection_path) if projection_path.exists() else {}
    trace_path = ARTIFACT_ROOT / "trace.jsonl"
    trace_rows = [
        json.loads(line)
        for line in trace_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    artifact_paths = [
        ARTIFACT_ROOT / "s3d_battery_runner_line30.py",
        ARTIFACT_ROOT / "s3d_part0_stop_report_generator.py",
        ARTIFACT_ROOT / "s3d_freshness_manifest_generator.py",
        ARTIFACT_ROOT / "s3d_compute_projection_line30.0.json",
        ARTIFACT_ROOT / "result.json",
        ARTIFACT_ROOT / "failure_manifest.json",
        ARTIFACT_ROOT / "s3d_battery_precondition_failure_manifest.json",
        ARTIFACT_ROOT / "trace.jsonl",
        ARTIFACT_ROOT / "trace.csv",
        ARTIFACT_ROOT / "s3d_certificate_report.json",
        ARTIFACT_ROOT / "s3d_null_env_report.json",
        ARTIFACT_ROOT / "baseline_comparison.json",
        ARTIFACT_ROOT / "ablation_report.json",
        ARTIFACT_ROOT / "replay_report.json",
        ARTIFACT_ROOT / "s3d_operator_bank_ops_proposal_line30.ps1",
        ARTIFACT_ROOT / "result_pre_ideal_repair_failure_v1.json",
        ARTIFACT_ROOT / "failure_manifest_pre_ideal_repair_failure_v1.json",
        ARTIFACT_ROOT / "trace_pre_ideal_repair_failure_v1.jsonl",
        ARTIFACT_ROOT / "trace_pre_ideal_repair_failure_v1.csv",
        ARTIFACT_ROOT / "s3d_compute_projection_line30.0_pre_ideal_repair_failure_v1.json",
        ARTIFACT_ROOT / "s3d_freshness_manifest_pre_ideal_repair_failure_v1.json",
    ]
    protected_before = failure.get("protected_artifacts_before", {})
    protected_after = failure.get("protected_artifacts_after", {})
    verdict = result.get("verdict")
    part0_stop = verdict == "STOP_s3d_part0_projection_exceeds_line"
    projected_cpu_hours = projection.get("projected_cpu_hours")
    line_cpu_hours = result.get("applied_cpu_hour_limit")
    projected_minus_line = (
        None
        if projected_cpu_hours is None or line_cpu_hours is None
        else float(projected_cpu_hours) - float(line_cpu_hours)
    )
    return {
        "task_id": TASK_ID,
        "task_card_id": "FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-EXEC-001A",
        "artifact": "s3d_freshness_manifest",
        "verdict": verdict,
        "stop_condition": result.get("stop_condition"),
        "claim_ceiling": (
            "S3d line-30 attempt freshness/readback only; no S3d certificate, NULL-env, "
            "environment-validity, gap, mechanism, learning, agency, EGO, or readiness claim"
        ),
        "producer_function": (
            "artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_freshness_manifest_generator.py::build_manifest"
        ),
        "run_started_at": result.get("run_started_at"),
        "run_finished_at": result.get("run_finished_at"),
        "run_wall_clock_seconds": result.get("run_wall_clock_seconds"),
        "run_process_cpu_seconds": result.get("run_process_cpu_seconds"),
        "total_contention_robust_cpu_hours": (
            None if result.get("run_process_cpu_seconds") is None else float(result["run_process_cpu_seconds"]) / 3600.0
        ),
        "part0_projection_summary": {
            "artifact": _artifact_ref(projection_path),
            "projected_cpu_hours": projected_cpu_hours,
            "signed_line_cpu_hours": line_cpu_hours,
            "projected_minus_line_cpu_hours": projected_minus_line,
            "decision": projection.get("decision"),
            "runtime_guard_decision": projection.get("runtime_guard_decision"),
            "process_cpu_seconds": projection.get("process_cpu_seconds"),
            "wall_clock_seconds": projection.get("wall_clock_seconds"),
            "run_id": projection.get("run_id"),
        },
        "parallelism_N": result.get("parallelism", {}).get(
            "n_workers",
            "not_applicable_part0_projection_stop" if part0_stop else "not_applicable_precondition_stop",
        ),
        "battery_units_completed": 0,
        "trace_rows": len(trace_rows),
        "member_rho_and_ci": [],
        "member_rho_and_ci_status": (
            "not_run_part0_projection_stop" if part0_stop else "not_run_precondition_stop"
        ),
        "cell_validity_guard": certificate.get(
            "cell_validity_guard",
            "not_run_part0_projection_stop" if part0_stop else "not_run_precondition_stop",
        ),
        "banked_artifact_bytes_unchanged": {
            "conclusion": failure.get("banked_stop_probe_artifacts_byte_unchanged"),
            "protected_artifacts_before": protected_before,
            "protected_artifacts_after": protected_after,
        },
        "result_failure_void_consistency": {
            "result_s3d_results_void": result.get("s3d_results_void"),
            "failure_manifest_s3d_results_void": failure.get("s3d_results_void"),
            "consistent": result.get("s3d_results_void") == failure.get("s3d_results_void"),
        },
        "artifact_hashes": [_artifact_ref(path) for path in artifact_paths],
        "verification_counts": {
            "py_compile_files_passed": int(py_compile_files),
            "pytest_items_passed": int(pytest_passed),
            "pytest_timeout_count": int(pytest_timeout_count),
        },
        "missing_due_stop": {
            "part0_projection_rerun_under_L30": (
                "ran_and_stopped_exceeds_line" if part0_stop else "not_run_precondition_stop"
            ),
            "full_should_win_battery": (
                "not_run_part0_projection_stop" if part0_stop else "not_run_precondition_stop"
            ),
            "null_env_battery": (
                "not_run_part0_projection_stop" if part0_stop else "not_run_precondition_stop"
            ),
        },
        "precondition_errors": result.get("precondition", {}).get("errors", []),
        "code_path_hash": _code_hash(
            [
                Path(__file__),
                ARTIFACT_ROOT / "s3d_battery_runner_line30.py",
                ARTIFACT_ROOT / "s3d_part0_stop_report_generator.py",
            ]
        ),
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--py-compile-files", type=int, required=True)
    parser.add_argument("--pytest-passed", type=int, required=True)
    parser.add_argument("--pytest-timeout-count", type=int, required=True)
    args = parser.parse_args()
    OUT.write_text(
        json.dumps(
            _jsonable(build_manifest(args.py_compile_files, args.pytest_passed, args.pytest_timeout_count)),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps(_artifact_ref(OUT), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
