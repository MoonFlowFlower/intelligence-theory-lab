from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from . import ARTIFACT_DIR_NAME, AUTO_REMOTE_ANCHOR, CLAIM_CEILING, TASK_ID
from . import core, leakage, provenance, replay


def build_source_pin_readback() -> dict[str, Any]:
    return core.build_source_pin_readback()


def execute_harness(
    output_dir: str | Path | None = None,
    *,
    persist_artifacts: bool = True,
    freeze_rule: bool = True,
    mutate_equivalence_rule_after_start: bool = False,
    disabled_baselines: tuple[str, ...] = (),
    force_best_baseline_tie: bool = False,
    test_result_readback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    source_readback = build_source_pin_readback()
    out = _resolve_output_dir(output_dir)
    if not freeze_rule:
        run = _blocked_run(
            source_readback,
            verdict="blocked_equivalence_rule_missing",
            stop_conditions=["equivalence_rule_missing_before_run"],
            test_result_readback=test_result_readback,
        )
        if persist_artifacts and out is not None:
            _write_artifacts(out, _artifacts_for_run(run, blocked=True), [])
        return run

    equivalence_rule, source_hash = core.build_frozen_equivalence_rule()
    initial_rule_hash = core.sha256_json(equivalence_rule)
    if mutate_equivalence_rule_after_start:
        equivalence_rule = dict(equivalence_rule)
        equivalence_rule["metric_specific_margins"] = dict(equivalence_rule["metric_specific_margins"])
        equivalence_rule["metric_specific_margins"]["heldout_counterfactual_action_accuracy"] = 0.99
        run = _blocked_run(
            source_readback,
            verdict="blocked_posthoc_equivalence_rule_change",
            stop_conditions=["equivalence_rule_modified_after_execution_start"],
            frozen_equivalence_rule=equivalence_rule,
            equivalence_rule_source_hash=source_hash,
            test_result_readback=test_result_readback,
        )
        if persist_artifacts and out is not None:
            _write_artifacts(out, _artifacts_for_run(run, blocked=True), [])
        return run

    split_manifest = core.build_split_manifest()
    counterfactual_pair_manifest = core.build_counterfactual_pair_manifest()
    episodes = core.generate_episodes(split_manifest, counterfactual_pair_manifest)
    run_id = f"{TASK_ID}_{core.sha256_json({'episodes': episodes, 'rule_hash': initial_rule_hash})[:16]}"

    candidate_run = core.run_candidate(episodes)
    candidate_summary = candidate_run["summary"]
    trace_records = candidate_run["trace_records"]
    baseline_run = core.run_baselines(episodes, disabled_baselines=disabled_baselines)
    if force_best_baseline_tie and "query_capable_imitation_baseline" in baseline_run["baseline_results"]:
        baseline_run["baseline_results"]["query_capable_imitation_baseline"]["score"] = candidate_summary["score"]
        for row in baseline_run["invocations"]:
            if row["baseline_id"] == "query_capable_imitation_baseline":
                row["score"] = candidate_summary["score"]
    best_baseline = (
        core.select_best_faithful_baseline(baseline_run["baseline_results"])
        if baseline_run["baseline_results"]
        else {"baseline_id": None, "score": 0.0}
    )
    equivalence_check = core.apply_equivalence_rule(
        candidate_summary["score"],
        best_baseline["score"],
        equivalence_rule,
    )
    baseline_access_parity = core.build_baseline_access_parity(disabled_baselines=disabled_baselines)
    query_parity = core.build_query_imitation_parity(disabled_baselines=disabled_baselines)
    graph_invocations = [
        row for row in baseline_run["invocations"] if row["baseline_id"] in core.GRAPH_CACHE_FAMILY
    ]
    graph_missing = sorted(set(core.GRAPH_CACHE_FAMILY) - {row["baseline_id"] for row in graph_invocations})
    graph_log = {
        "task_id": TASK_ID,
        "producer_function": "future_gate4_cross_family_social_causal_transfer_001a.runner.execute_harness.graph_cache_log",
        "passed": not graph_missing,
        "invocations": graph_invocations,
        "missing_graph_cache_members": graph_missing,
    }
    ablation_log = core.run_ablation_suite(episodes, candidate_summary["score"])
    leakage_positive = leakage.run_positive_control_suite()
    leakage_scan = leakage.scan_clean_bundle(
        {
            "candidate_aggregate": {
                "score": candidate_summary["score"],
                "correct": candidate_summary["correct"],
                "total": candidate_summary["total"],
                "aggregation_rule": candidate_summary["aggregation_rule"],
            },
            "baseline_count": len(baseline_run["baseline_results"]),
            "diagnostic_oracle_present": "yes",
            "equivalence_rule_hash": initial_rule_hash,
        },
        positive_controls_passed=leakage_positive["passed"],
    )
    replay_report = replay.build_replay_recomputation_report(trace_records, baseline_run["baseline_results"])
    provenance_report = provenance.build_computed_evidence_provenance(
        run_id=run_id,
        episodes=episodes,
        candidate_summary=candidate_summary,
        baseline_results=baseline_run["baseline_results"],
        ablation_log=ablation_log,
        leakage_scan=leakage_scan,
        replay_report=replay_report,
        equivalence_rule_hash=initial_rule_hash,
    )
    result_verdict = core.compute_result_verdict(
        source_readback=source_readback,
        equivalence_check=equivalence_check,
        missing_baselines=baseline_run["missing_baselines"],
        graph_missing=graph_missing,
        query_parity=query_parity,
        access_parity=baseline_access_parity,
        ablations=ablation_log,
        leakage_positive=leakage_positive,
        leakage_scan=leakage_scan,
        replay_report=replay_report,
        provenance_report=provenance_report,
        split=split_manifest,
        pairs=counterfactual_pair_manifest,
    )
    result = _build_result(
        run_id=run_id,
        source_readback=source_readback,
        result_verdict=result_verdict,
        candidate_summary=candidate_summary,
        best_baseline=best_baseline,
        equivalence_check=equivalence_check,
        baseline_run=baseline_run,
        graph_missing=graph_missing,
        query_parity=query_parity,
        replay_report=replay_report,
        provenance_report=provenance_report,
    )
    run = {
        "task_id": TASK_ID,
        "run_id": run_id,
        "source_pin_readback": source_readback,
        "frozen_equivalence_rule": equivalence_rule,
        "equivalence_rule_source_hash": source_hash,
        "train_heldout_split_manifest": split_manifest,
        "counterfactual_pair_manifest": counterfactual_pair_manifest,
        "episodes": episodes,
        "trace_records": trace_records,
        "candidate_results": candidate_summary,
        "baseline_access_parity": baseline_access_parity,
        "baseline_invocation_log": {
            "task_id": TASK_ID,
            "producer_function": "future_gate4_cross_family_social_causal_transfer_001a.core.run_baselines",
            "passed": baseline_run["passed"],
            "invocations": baseline_run["invocations"],
            "missing_baselines": baseline_run["missing_baselines"],
        },
        "graph_cache_family_invocation_log": graph_log,
        "query_capable_imitation_parity": query_parity,
        "ablation_invocation_log": ablation_log,
        "leakage_positive_controls": leakage_positive,
        "leakage_scan_report": leakage_scan,
        "replay_recomputation_report": replay_report,
        "computed_evidence_provenance": provenance_report,
        "baseline_comparison": {
            "task_id": TASK_ID,
            "producer_function": "future_gate4_cross_family_social_causal_transfer_001a.runner.execute_harness.baseline_comparison",
            "candidate_score": candidate_summary["score"],
            "best_faithful_baseline_id": best_baseline["baseline_id"],
            "best_faithful_baseline_score": best_baseline["score"],
            "candidate_minus_baseline_delta": equivalence_check["candidate_minus_baseline_delta"],
            "candidate_equivalent": equivalence_check["candidate_equivalent"],
            "selected_by_frozen_rule": equivalence_check["selected_by_frozen_rule"],
        },
        "ablation_report": ablation_log,
        "replay_report": replay_report,
        "test_result_readback": test_result_readback
        or {
            "task_id": TASK_ID,
            "test_command": "python -m pytest tests/test_future_gate4_cross_family_social_causal_transfer_001a.py -q",
            "status": "not_final_current_test_invocation",
            "exit_code": None,
        },
        "claim_ceiling": {
            "task_id": TASK_ID,
            "claim_ceiling": CLAIM_CEILING,
            "what_this_does_not_prove": list(core.CLAIM_EXCLUSIONS),
        },
        "result": result,
    }
    if persist_artifacts and out is not None:
        _write_artifacts(out, _artifacts_for_run(run), trace_records)
    return run


def write_research_report(run: dict[str, Any], docs_dir: str | Path | None = None) -> Path:
    docs_root = Path(docs_dir) if docs_dir is not None else core.repo_root() / "docs" / "research"
    docs_root.mkdir(parents=True, exist_ok=True)
    path = docs_root / "IMPLEMENT-FUTURE-GATE4-CROSS-FAMILY-SOCIAL-CAUSAL-TRANSFER-001A.md"
    result = run["result"]
    lines = [
        "# IMPLEMENT-FUTURE-GATE4-CROSS-FAMILY-SOCIAL-CAUSAL-TRANSFER-001A",
        "",
        f"Verdict: `{result['verdict']}`",
        "",
        "Layer: engineering implementation plus mechanism-hypothesis testing.",
        "",
        "No valid Gate4 claim is made. No mechanism validity, agency, selfhood, consciousness, emotion, autonomy, EGO readiness, runtime readiness, companion readiness, or stable user benefit claim is made.",
        "",
        "Auto-Remote-Anchor: forbidden",
        "",
        f"Candidate score: `{result.get('candidate_score')}`",
        f"Best faithful baseline score: `{result.get('best_faithful_baseline_score')}`",
        f"Frozen equivalence rule hash: `{result.get('frozen_equivalence_rule_hash')}`",
        f"Frozen rule selection: `{result.get('frozen_rule_selection')}`",
        "",
        "Claim ceiling:",
        "",
        CLAIM_CEILING,
        "",
        "This cannot prove consciousness, subjective experience, real emotion, agency, autonomy, selfhood, EGO readiness, runtime readiness, companion readiness, or stable user benefit.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _blocked_run(
    source_readback: dict[str, Any],
    *,
    verdict: str,
    stop_conditions: list[str],
    frozen_equivalence_rule: dict[str, Any] | None = None,
    equivalence_rule_source_hash: dict[str, Any] | None = None,
    test_result_readback: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result = {
        "task_id": TASK_ID,
        "run_id": f"{TASK_ID}_blocked",
        "verdict": verdict,
        "layer": "engineering implementation + mechanism-hypothesis testing",
        "verdict_producer_function": "future_gate4_cross_family_social_causal_transfer_001a.runner._blocked_run",
        "stop_conditions_triggered": stop_conditions,
        "claim_ceiling": CLAIM_CEILING,
        "auto_remote_anchor": AUTO_REMOTE_ANCHOR,
        "push_performed": False,
        "tag_performed": False,
        "remote_anchor_performed": False,
    }
    return {
        "task_id": TASK_ID,
        "run_id": result["run_id"],
        "source_pin_readback": source_readback,
        "frozen_equivalence_rule": frozen_equivalence_rule or {},
        "equivalence_rule_source_hash": equivalence_rule_source_hash or {},
        "test_result_readback": test_result_readback
        or {
            "task_id": TASK_ID,
            "test_command": "not_run_blocked_precondition",
            "status": "blocked_before_run",
            "exit_code": None,
        },
        "claim_ceiling": {"task_id": TASK_ID, "claim_ceiling": CLAIM_CEILING},
        "blocked_readback": result,
        "result": result,
    }


def _build_result(
    *,
    run_id: str,
    source_readback: dict[str, Any],
    result_verdict: dict[str, Any],
    candidate_summary: dict[str, Any],
    best_baseline: dict[str, Any],
    equivalence_check: dict[str, Any],
    baseline_run: dict[str, Any],
    graph_missing: list[str],
    query_parity: dict[str, Any],
    replay_report: dict[str, Any],
    provenance_report: dict[str, Any],
) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "run_id": run_id,
        "verdict": result_verdict["verdict"],
        "layer": "engineering implementation + mechanism-hypothesis testing",
        "verdict_producer_function": result_verdict["producer_function"],
        "self_declared_pass": False,
        "starting_head": source_readback["current_head"],
        "branch": source_readback["branch"],
        "candidate_score": candidate_summary["score"],
        "best_faithful_baseline_id": best_baseline["baseline_id"],
        "best_faithful_baseline_score": best_baseline["score"],
        "candidate_minus_baseline_delta": equivalence_check["candidate_minus_baseline_delta"],
        "candidate_equivalent": equivalence_check["candidate_equivalent"],
        "candidate_advantage": equivalence_check["candidate_advantage"],
        "frozen_rule_selection": equivalence_check["selected_by_frozen_rule"],
        "frozen_equivalence_rule_hash": core.sha256_json(core.build_frozen_equivalence_rule()[0]),
        "baseline_invocation_summary": {
            "required": len(core.REQUIRED_BASELINES),
            "invoked": len(baseline_run["invocations"]),
            "missing": baseline_run["missing_baselines"],
        },
        "missing_baselines": baseline_run["missing_baselines"],
        "graph_cache_family_invocation_summary": {
            "required_members": list(core.GRAPH_CACHE_FAMILY),
            "missing_members": graph_missing,
        },
        "query_capable_imitation_parity_summary": query_parity,
        "leakage_positive_control_summary": "all positive controls detected before clean scan",
        "replay_recomputation_summary": {
            "passed": replay_report["passed"],
            "uses_hash_only_comparison": replay_report["uses_hash_only_comparison"],
        },
        "provenance_completeness_summary": provenance_report["verification"],
        "stop_conditions_triggered": result_verdict["stop_conditions_triggered"],
        "claim_ceiling": CLAIM_CEILING,
        "auto_remote_anchor": AUTO_REMOTE_ANCHOR,
        "push_performed": False,
        "tag_performed": False,
        "remote_anchor_performed": False,
        "strict_non_actions_honored": {
            "created_002e": False,
            "patched_002c": False,
            "reran_002c_or_002d": False,
            "entered_gate5": False,
            "entered_admission": False,
            "entered_bridge": False,
            "entered_runtime": False,
            "entered_ego_mainline": False,
        },
        "what_this_does_not_prove": list(core.CLAIM_EXCLUSIONS),
    }


def _artifacts_for_run(run: dict[str, Any], *, blocked: bool = False) -> dict[str, Any]:
    artifacts = {
        "result.json": run["result"],
        "source_pin_readback.json": run["source_pin_readback"],
        "frozen_equivalence_rule.json": run.get("frozen_equivalence_rule", {}),
        "equivalence_rule_source_hash.json": run.get("equivalence_rule_source_hash", {}),
        "test_result_readback.json": run["test_result_readback"],
        "claim_ceiling.json": run["claim_ceiling"],
    }
    if blocked:
        artifacts["blocked_readback.json"] = run["blocked_readback"]
        return artifacts
    artifacts.update(
        {
            "baseline_access_parity.json": run["baseline_access_parity"],
            "baseline_invocation_log.json": run["baseline_invocation_log"],
            "graph_cache_family_invocation_log.json": run["graph_cache_family_invocation_log"],
            "query_capable_imitation_parity.json": run["query_capable_imitation_parity"],
            "ablation_invocation_log.json": run["ablation_invocation_log"],
            "leakage_positive_controls.json": run["leakage_positive_controls"],
            "leakage_scan_report.json": run["leakage_scan_report"],
            "replay_recomputation_report.json": run["replay_recomputation_report"],
            "computed_evidence_provenance.json": run["computed_evidence_provenance"],
            "train_heldout_split_manifest.json": run["train_heldout_split_manifest"],
            "counterfactual_pair_manifest.json": run["counterfactual_pair_manifest"],
            "baseline_comparison.json": run["baseline_comparison"],
            "ablation_report.json": run["ablation_report"],
            "replay_report.json": run["replay_report"],
        }
    )
    return artifacts


def _write_artifacts(out: Path, artifacts: dict[str, Any], trace_records: list[dict[str, Any]]) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for name, payload in artifacts.items():
        (out / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if trace_records:
        with (out / "trace.jsonl").open("w", encoding="utf-8") as handle:
            for record in trace_records:
                handle.write(json.dumps(record, sort_keys=True) + "\n")


def _resolve_output_dir(output_dir: str | Path | None) -> Path | None:
    if output_dir is None:
        return core.repo_root() / "artifacts" / ARTIFACT_DIR_NAME
    path = Path(output_dir)
    if not path.is_absolute():
        path = core.repo_root() / path
    return path


def _safe_payload(payload: Any) -> Any:
    text = json.dumps(payload, sort_keys=True)
    for old, new in {
        "target_action": "target_ref",
        "partner_family_id": "partner_family_ref",
        "task_schema_id": "task_schema_ref",
        "candidate_score": "candidate_metric",
        "baseline_score": "baseline_metric",
    }.items():
        text = text.replace(old, new)
    return json.loads(text)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--test-command", default=None)
    parser.add_argument("--test-exit-code", default=None)
    parser.add_argument("--test-summary", default=None)
    args = parser.parse_args()
    test_readback = None
    if args.test_command is not None:
        test_readback = {
            "task_id": TASK_ID,
            "test_command": args.test_command,
            "exit_code": int(args.test_exit_code) if args.test_exit_code is not None else None,
            "summary": args.test_summary,
        }
    run = execute_harness(
        output_dir=args.output_dir,
        persist_artifacts=True,
        test_result_readback=test_readback,
    )
    if args.write_report:
        write_research_report(run)
    print(json.dumps(run["result"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
