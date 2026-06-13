from __future__ import annotations

import json
from pathlib import Path
from typing import Any


FORBIDDEN_PATTERNS = {
    "ID leakage": ["\"seed\"", "\"context_id\"", "\"partner_id\""],
    "phase token leakage": ["phase_token", "\"phase\""],
    "bundle path leakage": ["bundle_path"],
    "oracle latent label leakage": ["oracle_latent_label"],
    "answer key leakage": ["answer_key"],
    "deterministic-order leakage": ["deterministic_order_key"],
    "future outcome leakage": ["future_outcome"],
    "split label leakage": ["split_label"],
}


def scan_bundle(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path)
    scanned_files = []
    excluded_paths = []
    detected = []
    for item in sorted(path.rglob("*")) if path.exists() else []:
        if not item.is_file():
            continue
        if item.suffix.lower() not in {".json", ".jsonl", ".txt"}:
            excluded_paths.append({"path": item.as_posix(), "status": "not_scanned"})
            continue
        text = item.read_text(encoding="utf-8")
        scanned_files.append(item.as_posix())
        detected.extend(_detect_in_text(text, item.as_posix()))
    categories = sorted({row["category"] for row in detected})
    return {
        "producer_function": "scan_bundle",
        "bundle_path_scanned": path.as_posix(),
        "scanned_files": scanned_files,
        "excluded_paths": excluded_paths,
        "detected_categories": categories,
        "detections": detected,
        "positive_control_detected": bool(categories),
        "unconditional_clean_report": False,
        "verdict": "blocked_by_leakage_scan" if categories else "clean",
    }


def scan_payload_bundle(payloads: dict[str, Any]) -> dict[str, Any]:
    detected = []
    for name, payload in payloads.items():
        text = json.dumps(payload, sort_keys=True)
        detected.extend(_detect_in_text(text, name))
    categories = sorted({row["category"] for row in detected})
    return {
        "producer_function": "scan_payload_bundle",
        "bundle_path_scanned": "in_memory_run_payloads",
        "scanned_files": sorted(payloads),
        "excluded_paths": [],
        "detected_categories": categories,
        "detections": detected,
        "positive_control_detected": bool(categories),
        "unconditional_clean_report": False,
        "verdict": "blocked_by_leakage_scan" if categories else "clean",
    }


def build_positive_control_report() -> dict[str, Any]:
    payload = {
        "seed": "seed_0",
        "context_id": "raw_context",
        "partner_id": "raw_partner",
        "phase_token": "train",
        "oracle_latent_label": "likes_direct",
        "answer_key": "direct_response",
        "deterministic_order_key": "row_000",
        "future_outcome": "success",
        "split_label": "heldout",
        "bundle_path": "artifacts/forbidden",
    }
    report = scan_payload_bundle({"positive_control.json": payload})
    report["positive_control_bundle"] = "deliberately_contaminated_in_memory_bundle"
    report["positive_control_detected"] = report["verdict"] == "blocked_by_leakage_scan"
    return report


def _detect_in_text(text: str, source: str) -> list[dict[str, str]]:
    rows = []
    for category, patterns in FORBIDDEN_PATTERNS.items():
        for pattern in patterns:
            if pattern in text:
                rows.append({"category": category, "pattern": pattern, "source": source})
                break
    return rows

