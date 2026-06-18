"""Provenance helpers: code-path hash, run id, per-metric provenance records,
and a static secret scan of the run path."""
from __future__ import annotations

import hashlib
import os
import re
import time
from typing import List

PKG_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_PATTERNS = [
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*=\s*['\"][^'\"]{12,}['\"]"),
]


def _py_files(root: str) -> List[str]:
    out = []
    for dirpath, _, files in os.walk(root):
        for f in sorted(files):
            if f.endswith(".py"):
                out.append(os.path.join(dirpath, f))
    return sorted(out)


def code_path_hash() -> str:
    h = hashlib.sha256()
    for fp in _py_files(PKG_DIR):
        with open(fp, "rb") as fh:
            h.update(fh.read())
    return h.hexdigest()


def run_id() -> str:
    return time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "_" + code_path_hash()[:8]


def secret_scan(extra_paths: List[str] = None) -> dict:
    """Scan the isolated run path (this package) for hardcoded secrets. Optionally
    also report on extra paths (e.g. scripts/push.*) WITHOUT blocking this local,
    artifact-only run if a secret lives outside the run path and is never invoked.
    """
    findings = {}
    for fp in _py_files(PKG_DIR):
        with open(fp, "r", errors="ignore") as fh:
            txt = fh.read()
        hits = [p.pattern for p in SECRET_PATTERNS if p.search(txt)]
        if hits:
            findings[fp] = hits
    report = {
        "run_path": PKG_DIR,
        "run_path_secret_findings": findings,
        "run_path_clean": (len(findings) == 0),
    }
    if extra_paths:
        extra = {}
        for fp in extra_paths:
            if os.path.exists(fp):
                with open(fp, "r", errors="ignore") as fh:
                    txt = fh.read()
                hits = [p.pattern for p in SECRET_PATTERNS if p.search(txt)]
                extra[fp] = hits
        report["extra_paths_scanned"] = extra
    return report


def provenance(producer_function: str, inputs, seeds, aggregation: str,
               rid: str) -> dict:
    return {
        "producer_function": producer_function,
        "inputs": inputs,
        "run_id": rid,
        "seed_episode_id": (f"{seeds[0]}..{seeds[-1]}" if seeds else None),
        "aggregation": aggregation,
        "code_path_hash": code_path_hash(),
    }
