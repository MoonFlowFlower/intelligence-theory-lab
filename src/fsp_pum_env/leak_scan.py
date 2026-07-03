"""Key/type leak scanner for S3a member-visible trajectory files."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import time
from typing import Any, Iterable, Mapping


LIMITATION_TEXT = (
    "Scanner is key/type-based; a real planted-VALUE leak mutant is a registered S4 obligation. "
    "This report must not be read as leak-proof."
)

FORBIDDEN_EXACT_KEYS = {
    "theta",
    "z",
    "latent",
    "latents",
    "latent_state",
    "session_state",
    "user_state",
    "trust",
    "trust_state",
    "style_map",
    "stable_fact_symbol",
    "controlled_theta",
    "response_distribution",
}

FORBIDDEN_KEY_FRAGMENTS = (
    "rng_seed",
    "master_seed",
    "env_seed",
    "seed",
    "trust_internal",
    "simulator_internal",
)


def scan_member_visible_files(paths: Iterable[str | Path]) -> dict[str, Any]:
    scanned = [Path(path) for path in paths]
    findings: list[dict[str, Any]] = []
    for path in scanned:
        for line_number, payload in _read_json_payloads(path):
            findings.extend(_scan_payload(payload, file=str(path), json_path=f"$[{line_number}]"))
    return {
        "passed": not findings,
        "scanned_files": [str(path) for path in scanned],
        "findings": findings,
        "scanner_kind": "key/type-based",
    }


def write_leak_scan_report(paths: Iterable[str | Path], output_path: str | Path) -> dict[str, Any]:
    run_started_at = _utc_timestamp()
    start = time.perf_counter()
    result = scan_member_visible_files(paths)
    report = {
        "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
        "stage": "S3a",
        "artifact": "s3a_leak_scan_report",
        "passed": result["passed"],
        "scanned_files": result["scanned_files"],
        "findings": result["findings"],
        "known_limitation": LIMITATION_TEXT,
        "claim": "key/type-based scan only; not leak-proof",
        "producer_function": "src.fsp_pum_env.leak_scan.write_leak_scan_report",
        "code_path_hash": _code_path_hash(),
        "run_started_at": run_started_at,
        "run_finished_at": _utc_timestamp(),
        "wall_clock_seconds": time.perf_counter() - start,
    }
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def write_leak_scan_report_from_manifest(manifest_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8-sig"))
    base = Path(manifest_path).parent
    member_visible = [base / path for path in manifest.get("member_visible_files", [])]
    report = write_leak_scan_report(member_visible, output_path)
    report["trajectory_manifest_path"] = str(manifest_path)
    report["recipe_mode_note"] = (
        "No raw member-visible trajectory files were persisted because the canonical raw view exceeds the S3a size ceiling; "
        "therefore this S3a scan covers persisted member-visible files only."
    )
    Path(output_path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def _read_json_payloads(path: Path) -> Iterable[tuple[int, Any]]:
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix == ".jsonl":
        for index, line in enumerate(text.splitlines(), start=1):
            if line.strip():
                yield index, json.loads(line)
        return
    yield 1, json.loads(text)


def _scan_payload(payload: Any, *, file: str, json_path: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            key_text = str(key)
            key_lower = key_text.lower()
            if key_lower in FORBIDDEN_EXACT_KEYS or any(fragment in key_lower for fragment in FORBIDDEN_KEY_FRAGMENTS):
                findings.append(
                    {
                        "file": file,
                        "json_path": f"{json_path}.{key_text}",
                        "matched_key": key_text,
                        "reason": "forbidden latent/seed/trust/simulator-internal key",
                    }
                )
            findings.extend(_scan_payload(value, file=file, json_path=f"{json_path}.{key_text}"))
        return findings
    if isinstance(payload, list):
        for index, value in enumerate(payload):
            findings.extend(_scan_payload(value, file=file, json_path=f"{json_path}[{index}]"))
    return findings


def _code_path_hash() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def _utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
