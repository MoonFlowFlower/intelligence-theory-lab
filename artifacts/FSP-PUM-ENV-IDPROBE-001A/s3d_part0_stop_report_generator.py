"""Generate canonical reports for an S3d PART-0 projection STOP.

This artifact-side generator is intentionally narrow: it does not rerun or
adjudicate certificate/NULL metrics.  It reads the already-emitted line-30
runner result plus PART-0 projection artifact and rewrites the canonical report
files so they describe the current fresh STOP rather than an older precondition
STOP.  The evidence claim remains the projection STOP only.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "FSP-PUM-ENV-IDPROBE-001A"
TASK_CARD_ID = "FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-EXEC-001A"
ARTIFACT_ROOT = ROOT / "artifacts" / TASK_ID

RESULT = ARTIFACT_ROOT / "result.json"
FAILURE_MANIFEST = ARTIFACT_ROOT / "failure_manifest.json"
PROJECTION = ARTIFACT_ROOT / "s3d_compute_projection_line30.0.json"
CERTIFICATE_REPORT = ARTIFACT_ROOT / "s3d_certificate_report.json"
NULL_ENV_REPORT = ARTIFACT_ROOT / "s3d_null_env_report.json"
BASELINE_COMPARISON = ARTIFACT_ROOT / "baseline_comparison.json"
ABLATION_REPORT = ARTIFACT_ROOT / "ablation_report.json"
REPLAY_REPORT = ARTIFACT_ROOT / "replay_report.json"
TRACE_JSONL = ARTIFACT_ROOT / "trace.jsonl"
TRACE_CSV = ARTIFACT_ROOT / "trace.csv"

CLAIM_CEILING = (
    "PART-0 projection STOP under line 30 and frozen 001B execution contract only; "
    "no S3d certificate, NULL-env, environment-validity, gap, mechanism, learning, "
    "agency, EGO, companion, or readiness claim"
)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _artifact_ref(path: Path) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "exists": path.exists(),
        "sha256": _sha256(path) if path.exists() else None,
        "size_bytes": path.stat().st_size if path.exists() else None,
    }


def _code_path_hash() -> str:
    h = hashlib.sha256()
    for path in [Path(__file__), ARTIFACT_ROOT / "s3d_battery_runner_line30.py"]:
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


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(_jsonable(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _stop_replay(result: Mapping[str, Any], projection: Mapping[str, Any]) -> dict[str, Any]:
    projected = float(projection["projected_cpu_hours"])
    line = float(result["applied_cpu_hour_limit"])
    recomputed_stop = projected > line
    expected_verdict = "STOP_s3d_part0_projection_exceeds_line"
    return {
        "producer_function": (
            "artifacts/FSP-PUM-ENV-IDPROBE-001A/"
            "s3d_part0_stop_report_generator.py::_stop_replay"
        ),
        "input_artifacts": [_artifact_ref(RESULT), _artifact_ref(PROJECTION)],
        "projection_artifact_decision": projection.get("decision"),
        "projected_cpu_hours": projected,
        "signed_line_cpu_hours": line,
        "projected_minus_line_cpu_hours": projected - line,
        "recomputed_relation": "exceeds_signed_line" if recomputed_stop else "within_signed_line",
        "expected_verdict_if_exceeds": expected_verdict,
        "result_verdict": result.get("verdict"),
        "verdict_match": bool(recomputed_stop and result.get("verdict") == expected_verdict),
        "run_id": projection.get("run_id"),
        "aggregation_rule": "projected_cpu_hours > signed_line_cpu_hours => STOP before full battery",
        "code_path_hash": _code_path_hash(),
    }


def build_reports() -> dict[str, Any]:
    result = _read_json(RESULT)
    failure = _read_json(FAILURE_MANIFEST)
    projection = _read_json(PROJECTION)
    replay = _stop_replay(result, projection)
    if not replay["verdict_match"]:
        raise RuntimeError(f"not_a_part0_projection_stop: {replay}")

    generated_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    protected_match = failure.get("banked_stop_probe_artifacts_byte_unchanged")
    common = {
        "task_id": TASK_ID,
        "task_card_id": TASK_CARD_ID,
        "stage": "S3d",
        "verdict": result.get("verdict"),
        "stop_condition": result.get("stop_condition"),
        "s3d_results_void": True,
        "claim_ceiling": CLAIM_CEILING,
        "precondition_passed": result.get("precondition", {}).get("passed"),
        "precondition_errors": result.get("precondition", {}).get("errors", []),
        "applied_cpu_hour_limit": result.get("applied_cpu_hour_limit"),
        "part0_projection": _artifact_ref(PROJECTION),
        "part0_projection_replay": replay,
        "banked_stop_probe_artifacts_byte_unchanged": protected_match,
        "run_started_at": result.get("run_started_at"),
        "run_finished_at": result.get("run_finished_at"),
        "generated_at_utc": generated_at,
        "producer_function": (
            "artifacts/FSP-PUM-ENV-IDPROBE-001A/"
            "s3d_part0_stop_report_generator.py::build_reports"
        ),
        "code_path_hash": _code_path_hash(),
    }

    certificate_report = {
        **common,
        "artifact": "s3d_certificate_report",
        "rows": [],
        "member_rho_and_ci": [],
        "member_rho_and_ci_status": "not_run_part0_projection_stop",
        "cell_validity_guard": {
            "status": "not_run_part0_projection_stop",
            "reason": "PART-0 projection exceeded signed L=30 before ideal/member cell scoring.",
            "guard_basis": "001B k×SE, k=5",
        },
        "not_run_reason": "PART-0 projection exceeded signed L=30; no should-win member rho or CI was scored.",
    }
    null_report = {
        **common,
        "artifact": "s3d_null_env_report",
        "rows": [],
        "breaches": [],
        "false_headroom_status": "not_run_part0_projection_stop",
        "not_run_reason": "PART-0 projection exceeded signed L=30; NULL-env was not scored.",
    }
    baseline_report = {
        **common,
        "artifact": "baseline_comparison",
        "comparison_scope": "not_run_part0_projection_stop",
        "baseline_results": [],
        "not_run_reason": "PART-0 projection exceeded signed L=30 before baseline/member battery launch.",
    }
    ablation_report = {
        **common,
        "artifact": "ablation_report",
        "ablation_scope": "not_run_part0_projection_stop",
        "cert_only_variants": "not_run_part0_projection_stop",
        "base_invariance_regression": "not_run_part0_projection_stop",
        "not_run_reason": "PART-0 projection exceeded signed L=30 before BASE-invariance and cert-only variant runs.",
    }
    replay_report = {
        **common,
        "artifact": "replay_report",
        "replay_scope": "PART-0 projection STOP only; no scored should-win/NULL trace exists to replay.",
        "verdict_match": replay["verdict_match"],
        "full_battery_replay": "not_run_part0_projection_stop",
        "not_run_reason": "PART-0 projection exceeded signed L=30 before scored battery trace generation.",
    }
    trace_row = {
        "event_type": "part0_projection_stop",
        "unit_id": "part0::line30.0",
        "unit_type": "part0_projection",
        "phase": "preflight",
        "member": "none",
        "cell_id": "none",
        "metric": None,
        "rho": None,
        "ci95": None,
        "projected_cpu_hours": projection.get("projected_cpu_hours"),
        "signed_line_cpu_hours": result.get("applied_cpu_hour_limit"),
        "projected_minus_line_cpu_hours": replay["projected_minus_line_cpu_hours"],
        "process_cpu_seconds": projection.get("process_cpu_seconds"),
        "wall_clock_seconds": projection.get("wall_clock_seconds"),
        "contention_robust_cpu_hours": (
            None
            if projection.get("process_cpu_seconds") is None
            else float(projection["process_cpu_seconds"]) / 3600.0
        ),
        "wall_clock_based_cpu_hours": (
            None
            if projection.get("wall_clock_seconds") is None
            else float(projection["wall_clock_seconds"]) / 3600.0
        ),
        "heldout_users_800_999_touched": False,
        "future_observations_used": False,
        "verdict": result.get("verdict"),
        "stop_condition": result.get("stop_condition"),
        "s3d_results_void": True,
        "run_id": projection.get("run_id"),
        "producer_function": (
            "artifacts/FSP-PUM-ENV-IDPROBE-001A/"
            "s3d_part0_stop_report_generator.py::build_reports"
        ),
        "code_path_hash": _code_path_hash(),
        "generated_at_utc": generated_at,
    }

    return {
        "certificate_report": certificate_report,
        "null_env_report": null_report,
        "baseline_comparison": baseline_report,
        "ablation_report": ablation_report,
        "replay_report": replay_report,
        "trace_row": trace_row,
    }


def write_reports() -> dict[str, Any]:
    reports = build_reports()
    _write_json(CERTIFICATE_REPORT, reports["certificate_report"])
    _write_json(NULL_ENV_REPORT, reports["null_env_report"])
    _write_json(BASELINE_COMPARISON, reports["baseline_comparison"])
    _write_json(ABLATION_REPORT, reports["ablation_report"])
    _write_json(REPLAY_REPORT, reports["replay_report"])

    row = reports["trace_row"]
    TRACE_JSONL.write_text(json.dumps(_jsonable(row), sort_keys=True) + "\n", encoding="utf-8")
    with TRACE_CSV.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(row.keys()))
        writer.writeheader()
        writer.writerow(_jsonable(row))

    return {
        "producer_function": (
            "artifacts/FSP-PUM-ENV-IDPROBE-001A/"
            "s3d_part0_stop_report_generator.py::write_reports"
        ),
        "written": [
            _artifact_ref(CERTIFICATE_REPORT),
            _artifact_ref(NULL_ENV_REPORT),
            _artifact_ref(BASELINE_COMPARISON),
            _artifact_ref(ABLATION_REPORT),
            _artifact_ref(REPLAY_REPORT),
            _artifact_ref(TRACE_JSONL),
            _artifact_ref(TRACE_CSV),
        ],
        "code_path_hash": _code_path_hash(),
    }


def main() -> int:
    print(json.dumps(write_reports(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
