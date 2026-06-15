from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any


TASK_ID = "GATE1-FAILED-GRAPH-CACHE-RECONCILIATION-001A"
QUEUE_ID = "POST-FREEZE-GATE0-3-SEQUENTIAL-REPAIR-QUEUE-001A"
SELECTED_ITEM = "GATE1-FAILED-GRAPH-CACHE-RECONCILIATION"
ARTIFACT_DIR_REL = (
    "artifacts/"
    "post_freeze_gate0_3_sequential_repair_queue_001a_gate1_failed_graph_cache_reconciliation"
)
CLAIM_CEILING = (
    "Gate1 failed graph-cache reconciliation and post-freeze queue selection only; "
    "no Gate1 pass, mechanism-validity, bridge, admission, runtime, or EGO-readiness claim"
)
VERDICT_PRESERVE_CLOSURE = (
    "gate1_failed_graph_cache_reconciliation_001a_preserve_failed_graph_cache_collapse"
)
SEEDS = [11, 13, 17, 19, 23]

PRIOR_GATE1_ARTIFACT_REL = "artifacts/gate1_replay_consolidation_exec_taskcard_001"
GATE1_001C_ARTIFACT_REL = "artifacts/gate1_replay_consolidation_001c_executable_preflight"
PRIOR_CLOSEOUT_REL = "docs/GATE1-REPLAY-CONSOLIDATION-LINEAGE-CLOSEOUT-001.md"

GRAPH_CACHE_CONTROLS = [
    "graph_lookup",
    "transition_table",
    "successor_map",
    "predecessor_map",
    "fsm_planner",
    "count_table",
    "compressed_map",
    "episodic_traversal",
]
WINDOW_CACHE_CONTROLS = [
    "hidden_state_cache",
    "prefix_cache",
    "longer_context_retrieval",
    "sequence_lookup",
    "nn_sequence",
]
ABLATION_VARIANT_PREFIXES = [
    "A_cand_salience_pe",
    "A_cand_reverse",
    "B_cand_salience_pe",
    "B_cand_reverse",
    "B_ctrl_shuffled_replay_B",
]
NOT_SELECTED_ITEMS = [
    "Gate3 baseline/ablation repair",
    "integrated Gate0-Gate3 testbed repair",
    "Gate4 work",
    "bridge/admission/runtime work",
    "unrelated files",
]
DOWNSTREAM_AUTHORIZATION = {
    "gate1_pass": False,
    "gate3": False,
    "integrated_testbed": False,
    "gate4": False,
    "bridge": False,
    "admission": False,
    "runtime": False,
    "ego_mainline": False,
}


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_json(output_dir: Path, name: str, data: Any) -> None:
    (output_dir / name).write_text(
        json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _completed_run_ids(ledger_rows: list[dict[str, Any]]) -> set[str]:
    return {
        row["run_id"]
        for row in ledger_rows
        if row.get("status") == "completed" and isinstance(row.get("run_id"), str)
    }


def _extract_closeout_fields(text: str) -> dict[str, str]:
    wanted = {
        "parent_gate1_package_verdict",
        "candidate_A_status",
        "candidate_B_residue_status",
        "same_agent_bridge_status",
        "next_allowed_direction",
        "claim_ceiling",
    }
    fields: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^([A-Za-z0-9_]+)\s*=\s*(.+)$", line.strip())
        if match and match.group(1) in wanted:
            fields[match.group(1)] = match.group(2).strip()
    return fields


def _run_id_evidence(prefix: str, completed: set[str]) -> dict[str, Any]:
    run_ids = [f"{prefix}_seed{seed}" for seed in SEEDS]
    missing = [run_id for run_id in run_ids if run_id not in completed]
    return {
        "variant_prefix": prefix,
        "producer_function": "run_ledger_completed_run_id_check",
        "seeds": SEEDS,
        "completed_run_ids": [run_id for run_id in run_ids if run_id in completed],
        "missing_run_ids": missing,
        "completed_for_all_seeds": not missing,
    }


def _code_path_hashes(repo_root: Path) -> dict[str, str]:
    runner = repo_root / "src" / "gate1_preflight" / "runner.py"
    core = repo_root / "src" / "gate1_preflight" / "core.py"
    reconciliation = repo_root / "src" / "gate1_failed_graph_cache_reconciliation_001a" / "runner.py"
    return {
        "gate1_preflight_runner_py": _sha256_file(runner),
        "gate1_preflight_core_py": _sha256_file(core),
        "gate1_reconciliation_runner_py": _sha256_file(reconciliation),
    }


def _git_value(repo_root: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"
    return result.stdout.strip()


def build_baseline_reconciliation(
    prior_result: dict[str, Any],
    prior_baseline: dict[str, Any],
    completed: set[str],
) -> dict[str, Any]:
    del prior_baseline
    matched_graph = sorted(
        control
        for control in prior_result["candidate_A_matched_by"]["graph_cache"]
        if control in GRAPH_CACHE_CONTROLS
    )
    graph_ledger_evidence = [
        _run_id_evidence(f"A_ctrl_{control}", completed) for control in GRAPH_CACHE_CONTROLS
    ]
    window_ledger_evidence = [
        _run_id_evidence(f"B_ctrl_{control}", completed) for control in WINDOW_CACHE_CONTROLS
    ]
    window_executed = all(row["completed_for_all_seeds"] for row in window_ledger_evidence)
    graph_matched = bool(matched_graph)
    generic_matched = bool(prior_result["candidate_A_matched_by"]["generic_replay"])
    b_generic_matched = bool(prior_result["candidate_B_matched_by"]["generic_replay"])
    return {
        "task_id": TASK_ID,
        "producer_function": "build_baseline_reconciliation",
        "prior_artifact": f"{PRIOR_GATE1_ARTIFACT_REL}/baseline_comparison.json",
        "prior_result_artifact": f"{PRIOR_GATE1_ARTIFACT_REL}/result.json",
        "package_verdict": prior_result["package_verdict"],
        "candidate_A_graph_cache_collapse_detected": graph_matched,
        "candidate_A_matched_by_graph_cache_family": matched_graph,
        "candidate_A_matched_by_generic_replay": sorted(
            prior_result["candidate_A_matched_by"]["generic_replay"]
        ),
        "candidate_B_matched_by_generic_replay": sorted(
            prior_result["candidate_B_matched_by"]["generic_replay"]
        ),
        "graph_cache_control_ledger_evidence": graph_ledger_evidence,
        "window_cache_control_ledger_evidence": window_ledger_evidence,
        "candidate_B_window_cache_controls_executed": window_executed,
        "fair_control_match_blocks_positive_gate1_claim": bool(
            graph_matched or generic_matched or b_generic_matched
        ),
        "aggregation_rule": (
            "preserve failed_graph_cache_collapse when prior callable controls matched or "
            "beat candidate under the frozen zero-advantage lineage rule"
        ),
        "claim_ceiling": CLAIM_CEILING,
    }


def build_ablation_reconciliation(
    prior_ablation: dict[str, Any],
    completed: set[str],
) -> dict[str, Any]:
    ledger_evidence = [_run_id_evidence(prefix, completed) for prefix in ABLATION_VARIANT_PREFIXES]
    has_expected_sections = all(
        key in prior_ablation
        for key in [
            "A_salience_pe_vs_chrono",
            "A_reverse_vs_chrono",
            "B_salience_pe_vs_chrono",
            "B_reverse_vs_chrono",
            "B_shuffled_vs_chrono",
        ]
    )
    all_completed = all(record["completed_for_all_seeds"] for record in ledger_evidence)
    return {
        "task_id": TASK_ID,
        "producer_function": "build_ablation_reconciliation",
        "prior_artifact": f"{PRIOR_GATE1_ARTIFACT_REL}/ablation_report.json",
        "verified_ablation_variant_prefixes": ABLATION_VARIANT_PREFIXES,
        "ablation_variant_ledger_evidence": ledger_evidence,
        "prior_ablation_sections_present": has_expected_sections,
        "all_required_ablation_variants_have_completed_ledger_runs": all_completed,
        "real_ablation_rerun_evidence_verified": bool(has_expected_sections and all_completed),
        "aggregation_rule": (
            "verify prior ablation report sections against completed candidate or control "
            "variant run IDs for all frozen seeds"
        ),
        "claim_ceiling": CLAIM_CEILING,
    }


def build_lineage_reconciliation(
    repo_root: Path,
    prior_result: dict[str, Any],
    baseline: dict[str, Any],
    ablation: dict[str, Any],
    gate1_001c_result: dict[str, Any],
    gate1_001c_baseline: dict[str, Any],
    gate1_001c_ablation: dict[str, Any],
    closeout_fields: dict[str, str],
    source_hashes: dict[str, str],
    completed: set[str],
) -> dict[str, Any]:
    gate1_001c_literal_surface = {
        "result_verdict": gate1_001c_result.get("verdict"),
        "baseline_has_producer_function": "producer_function" in gate1_001c_baseline,
        "ablation_has_producer_function": "producer_function" in gate1_001c_ablation,
        "baseline_rows_claim_executed": all(
            row.get("executed") is True for row in gate1_001c_baseline.get("baselines", [])
        ),
        "ablation_rows_claim_executed": all(
            row.get("executed") is True for row in gate1_001c_ablation.get("ablations", [])
        ),
    }
    graph_verified = sorted(
        evidence["variant_prefix"].replace("A_ctrl_", "")
        for evidence in baseline["graph_cache_control_ledger_evidence"]
        if evidence["completed_for_all_seeds"]
        and evidence["variant_prefix"].replace("A_ctrl_", "") in baseline["candidate_A_matched_by_graph_cache_family"]
    )
    window_verified = sorted(
        evidence["variant_prefix"].replace("B_ctrl_", "")
        for evidence in baseline["window_cache_control_ledger_evidence"]
        if evidence["completed_for_all_seeds"]
    )
    fair_controls_match = baseline["fair_control_match_blocks_positive_gate1_claim"]
    real_ablation_verified = ablation["real_ablation_rerun_evidence_verified"]
    return {
        "task_id": TASK_ID,
        "queue_id": QUEUE_ID,
        "selected_item": SELECTED_ITEM,
        "prior_lineage_result": {
            "task_id": prior_result["task_id"],
            "package_verdict": prior_result["package_verdict"],
            "candidate_A_pass": prior_result["candidate_A_pass"],
            "candidate_B_pass": prior_result["candidate_B_pass"],
            "candidate_A_matched_by": prior_result["candidate_A_matched_by"],
            "candidate_B_matched_by": prior_result["candidate_B_matched_by"],
        },
        "prior_lineage_closeout": closeout_fields,
        "gate1_001c_literal_surface": gate1_001c_literal_surface,
        "gate1_001c_literal_pass_not_upgraded": bool(
            gate1_001c_result.get("verdict") == "gate1_replay_consolidation_001c_bounded_preflight_pass"
            and not gate1_001c_literal_surface["baseline_has_producer_function"]
            and not gate1_001c_literal_surface["ablation_has_producer_function"]
        ),
        "graph_cache_family_controls_verified": graph_verified,
        "window_cache_controls_verified": window_verified,
        "completed_ledger_run_count": len(completed),
        "fair_controls_match_or_beat_candidate": fair_controls_match,
        "real_ablation_rerun_evidence_verified": real_ablation_verified,
        "closure_preserved": bool(
            prior_result["package_verdict"] == "gate1_preflight_failed_graph_cache_collapse"
            and closeout_fields.get("parent_gate1_package_verdict") == "failed_graph_cache_collapse"
            and fair_controls_match
            and real_ablation_verified
        ),
        "positive_gate1_inheritance_allowed": False,
        "source_artifact_hashes": source_hashes,
        "code_path_hashes": _code_path_hashes(repo_root),
        "claim_ceiling": CLAIM_CEILING,
    }


def run_reconciliation(repo_root: Path | str, output_dir: Path | str) -> dict[str, Any]:
    repo = Path(repo_root)
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    prior_dir = repo / PRIOR_GATE1_ARTIFACT_REL
    gate1_001c_dir = repo / GATE1_001C_ARTIFACT_REL
    closeout_path = repo / PRIOR_CLOSEOUT_REL

    prior_result_path = prior_dir / "result.json"
    prior_baseline_path = prior_dir / "baseline_comparison.json"
    prior_ablation_path = prior_dir / "ablation_report.json"
    prior_ledger_path = prior_dir / "run_ledger.jsonl"
    prior_replay_path = prior_dir / "replay_report.json"
    gate1_001c_result_path = gate1_001c_dir / "result.json"
    gate1_001c_baseline_path = gate1_001c_dir / "baseline_comparison.json"
    gate1_001c_ablation_path = gate1_001c_dir / "ablation_report.json"

    prior_result = _read_json(prior_result_path)
    prior_baseline = _read_json(prior_baseline_path)
    prior_ablation = _read_json(prior_ablation_path)
    prior_ledger = _read_jsonl(prior_ledger_path)
    gate1_001c_result = _read_json(gate1_001c_result_path)
    gate1_001c_baseline = _read_json(gate1_001c_baseline_path)
    gate1_001c_ablation = _read_json(gate1_001c_ablation_path)
    closeout_fields = _extract_closeout_fields(closeout_path.read_text(encoding="utf-8"))

    source_hashes = {
        "prior_result_json": _sha256_file(prior_result_path),
        "prior_baseline_comparison_json": _sha256_file(prior_baseline_path),
        "prior_ablation_report_json": _sha256_file(prior_ablation_path),
        "prior_run_ledger_jsonl": _sha256_file(prior_ledger_path),
        "prior_replay_report_json": _sha256_file(prior_replay_path),
        "prior_lineage_closeout_md": _sha256_file(closeout_path),
        "gate1_001c_result_json": _sha256_file(gate1_001c_result_path),
        "gate1_001c_baseline_comparison_json": _sha256_file(gate1_001c_baseline_path),
        "gate1_001c_ablation_report_json": _sha256_file(gate1_001c_ablation_path),
    }
    completed = _completed_run_ids(prior_ledger)

    selected_item = {
        "task_id": TASK_ID,
        "queue_id": QUEUE_ID,
        "max_queue_items_per_run": 1,
        "selected_item": SELECTED_ITEM,
        "selected_item_count": 1,
        "not_selected_items": NOT_SELECTED_ITEMS,
        "selection_reason": (
            "next unresolved frozen item after anchored Gate2 ablation repair; "
            "Gate1 must first reconcile against failed_graph_cache_collapse"
        ),
        "claim_ceiling": CLAIM_CEILING,
    }
    baseline = build_baseline_reconciliation(prior_result, prior_baseline, completed)
    ablation = build_ablation_reconciliation(prior_ablation, completed)
    lineage = build_lineage_reconciliation(
        repo,
        prior_result,
        baseline,
        ablation,
        gate1_001c_result,
        gate1_001c_baseline,
        gate1_001c_ablation,
        closeout_fields,
        source_hashes,
        completed,
    )

    stop_conditions = []
    if not lineage["closure_preserved"]:
        stop_conditions.append("gate1_failed_graph_cache_lineage_not_verified")
    if selected_item["selected_item"] != SELECTED_ITEM or selected_item["selected_item_count"] != 1:
        stop_conditions.append("queue_selection_scope_violation")

    result = {
        "task_id": TASK_ID,
        "queue_id": QUEUE_ID,
        "verdict": VERDICT_PRESERVE_CLOSURE if not stop_conditions else "gate1_failed_graph_cache_reconciliation_001a_blocked",
        "current_layer": "engineering implementation / evidence-governance only",
        "mainline_integration_status": "none",
        "enabled_status": "no enabled path",
        "real_trigger_evidence": (
            "anchored Gate2 ablation repair plus frozen Gate1 001C literal-pass issue "
            "and prior failed_graph_cache_collapse lineage"
        ),
        "claim_ceiling": CLAIM_CEILING,
        "artifact_dir": ARTIFACT_DIR_REL,
        "max_queue_items_per_run": 1,
        "selected_item_count": 1,
        "selected_items": [SELECTED_ITEM],
        "prior_lineage_package_verdict": prior_result["package_verdict"],
        "gate1_001c_literal_pass_not_upgraded": lineage["gate1_001c_literal_pass_not_upgraded"],
        "fair_controls_match_or_beat_candidate": lineage["fair_controls_match_or_beat_candidate"],
        "real_ablation_rerun_evidence_verified": lineage["real_ablation_rerun_evidence_verified"],
        "closure_preserved": lineage["closure_preserved"],
        "positive_gate1_inheritance_allowed": False,
        "downstream_authorization": DOWNSTREAM_AUTHORIZATION,
        "stop_conditions_triggered": stop_conditions,
        "git_readback": {
            "head": _git_value(repo, "rev-parse", "HEAD"),
            "branch": _git_value(repo, "branch", "--show-current"),
            "status_short": _git_value(repo, "status", "--short"),
        },
        "what_this_does_not_prove": [
            "Gate1 pass",
            "Gate3 repaired",
            "integrated testbed repaired",
            "Gate4 repaired",
            "bridge readiness",
            "admission readiness",
            "runtime readiness",
            "EGO readiness",
            "mechanism validity",
            "agency",
            "consciousness",
            "subjectivity",
            "real emotion",
            "autonomy",
            "stable user benefit",
        ],
    }

    readback = {
        "task_id": TASK_ID,
        "artifact_dir": ARTIFACT_DIR_REL,
        "artifact_files": sorted(
            [
                "selected_item.json",
                "lineage_reconciliation.json",
                "baseline_comparison.json",
                "ablation_report.json",
                "result.json",
                "readback.json",
                "claim_ceiling.txt",
            ]
        ),
        "source_artifact_hashes": source_hashes,
        "claim_ceiling": CLAIM_CEILING,
        "changed_scope": [
            "docs/research/GATE1-FAILED-GRAPH-CACHE-RECONCILIATION-001A.md",
            "src/gate1_failed_graph_cache_reconciliation_001a/",
            "tests/test_gate1_failed_graph_cache_reconciliation_001a.py",
            ARTIFACT_DIR_REL + "/",
        ],
    }

    _write_json(output, "selected_item.json", selected_item)
    _write_json(output, "baseline_comparison.json", baseline)
    _write_json(output, "ablation_report.json", ablation)
    _write_json(output, "lineage_reconciliation.json", lineage)
    _write_json(output, "result.json", result)
    _write_json(output, "readback.json", readback)
    (output / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")

    return result
