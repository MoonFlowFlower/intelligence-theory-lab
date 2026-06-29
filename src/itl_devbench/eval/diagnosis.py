from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def write_oracle_headroom_diagnosis(
    path: str | Path,
    manifest: Dict[str, Any],
    oracle_headroom_report: Dict[str, Any],
    graph_cache_audit: Dict[str, Any],
    previous_invalid_run: str = "RUN_20260629T151318Z",
) -> None:
    aggregate = oracle_headroom_report["aggregate"]
    lines = [
        "# ITL-DEV-BENCH-001B Oracle Headroom Diagnosis",
        "",
        f"Current run: {manifest.get('run_id')}",
        f"Previous invalid benchmark-validation evidence preserved: {previous_invalid_run}",
        "",
        "Layer: benchmark validation and engineering repair only.",
        "Claim ceiling: benchmark/headroom repair only.",
        "",
        "Diagnosis:",
        "- The prior oracle control was hidden-state-aware but not objective-aligned.",
        "- The primary metric is `total_reward` with higher-is-better orientation.",
        "- A hidden-state upper control must choose actions that optimize that same reward objective, including waiting when movement has negative expected value.",
        "",
        "Repair:",
        "- Oracle action selection now evaluates legal safe paths by net reward under hidden rules.",
        "- Candidate minimal-loop policy and PE/memory/planner variants are unchanged.",
        "- Graph-cache remains a frozen observation/outcome baseline and is audited for access scope.",
        "",
        f"Graph-cache audit verdict: {graph_cache_audit.get('verdict')}",
        f"Aggregate oracle headroom valid: {aggregate.get('oracle_upper_bound_valid')}",
        f"Aggregate oracle score: {aggregate.get('oracle_score')}",
        f"Aggregate baseline scores: {aggregate.get('baseline_scores')}",
        "",
        "If any stage violates oracle headroom, the benchmark remains invalid for candidate claims.",
    ]
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
