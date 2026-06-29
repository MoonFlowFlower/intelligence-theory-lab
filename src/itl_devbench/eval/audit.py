from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from itl_devbench.core.trace import read_jsonl, validate_hash_chain
from itl_devbench.envs.families import REQUIRED_FAMILY_IDS
from itl_devbench.eval.report import ALLOWED_VERDICTS
from itl_devbench.eval.run_matrix import REQUIRED_BASELINES, REQUIRED_MINIMAL_LOOP_VARIANTS

FORBIDDEN_CLAIM_STRINGS = [
    "consciousness",
    "emotion",
    "subjective",
    "autonomous",
    "agency",
    "electronic life",
    "joi-ready",
    "joi-like",
    "ego ready",
    "mechanism valid",
    "validated learning",
    "true self",
]

REQUIRED_SOURCE_HASH_SUFFIXES = [
    "src/itl_devbench/envs/developmental_grid.py",
    "src/itl_devbench/envs/families.py",
    "src/itl_devbench/envs/task_family_generator.py",
    "src/itl_devbench/agents/minimal_loop.py",
    "src/itl_devbench/agents/random_policy.py",
    "src/itl_devbench/agents/obs_only_policy.py",
    "src/itl_devbench/agents/generic_fsm.py",
    "src/itl_devbench/agents/graph_cache.py",
    "src/itl_devbench/agents/oracle.py",
    "src/itl_devbench/eval/run_matrix.py",
    "src/itl_devbench/eval/replay.py",
    "src/itl_devbench/eval/metrics.py",
    "src/itl_devbench/eval/audit.py",
    "src/itl_devbench/eval/family_metrics.py",
    "src/itl_devbench/eval/saturation.py",
    "src/itl_devbench/eval/diagnosis.py",
    "src/itl_devbench/eval/graph_cache_audit.py",
    "src/itl_devbench/eval/headroom.py",
    "src/itl_devbench/eval/report.py",
]


def audit_manifest(manifest_path: str | Path) -> Dict[str, Any]:
    manifest_path = Path(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    run_dir = manifest_path.parent
    trace_path = _resolve_path(run_dir, manifest["trace_path"])
    report_path = _resolve_path(run_dir, manifest["report_path"])
    oracle_headroom_path = _resolve_path(run_dir, manifest.get("oracle_headroom_report_path", "oracle_headroom_report.json"))
    graph_cache_audit_path = _resolve_path(
        run_dir, manifest.get("leakage_audit_graph_cache_path", "leakage_audit_graph_cache.json")
    )
    events = read_jsonl(trace_path)
    report_text = report_path.read_text(encoding="utf-8")
    oracle_headroom = _read_json_if_exists(oracle_headroom_path)
    graph_cache_audit = _read_json_if_exists(graph_cache_audit_path)
    generator_enabled = bool(manifest.get("task_family_generator_001c_enabled"))
    generator_spec = _read_manifest_json(run_dir, manifest, "generator_spec_001c_path") if generator_enabled else {}
    family_summary = _read_manifest_json(run_dir, manifest, "family_metric_summary_path") if generator_enabled else {}
    graph_saturation = _read_manifest_json(run_dir, manifest, "graph_cache_saturation_report_path") if generator_enabled else {}
    candidate_hash_check = _read_manifest_json(run_dir, manifest, "candidate_source_hash_check_path") if generator_enabled else {}
    checks: list[Dict[str, Any]] = []

    _add_check(checks, "forbidden_claim_strings_absent", _forbidden_claims_absent(report_text))
    _add_check(checks, "candidate_traces_do_not_contain_hidden_state", _candidate_traces_hide_state(events))
    _add_check(checks, "oracle_trace_clearly_labeled", all(e["agent_kind"] == "oracle" for e in events if e["agent_id"] == "oracle"))
    _add_check(checks, "pre_action_prediction_exists", all(e.get("pre_action_prediction") is not None for e in events if e["agent_id"] != "random_policy"))
    _add_check(checks, "pre_action_prediction_order_before_env_result", _prediction_order_before_env_result(trace_path))
    chain_ok, chain_errors = validate_hash_chain(events)
    _add_check(checks, "event_hash_chain_valid", chain_ok, chain_errors)
    variants = {e["variant"] for e in events if e["agent_id"] == "minimal_loop"}
    _add_check(checks, "all_minimal_loop_variants_present", variants == set(REQUIRED_MINIMAL_LOOP_VARIANTS), sorted(variants))
    baselines = {e["agent_id"] for e in events if e["agent_kind"] == "baseline"}
    _add_check(checks, "all_required_frozen_baselines_present", set(REQUIRED_BASELINES).issubset(baselines), sorted(baselines))
    _add_check(checks, "graph_cache_oracle_not_mislabeled_as_candidate", _baseline_labels_valid(events))
    _add_check(checks, "oracle_headroom_report_exists", bool(oracle_headroom))
    _add_check(
        checks,
        "oracle_headroom_upper_bound_valid_or_explicit_invalid",
        _headroom_valid_or_explicit_invalid(oracle_headroom, manifest),
        oracle_headroom.get("aggregate") if oracle_headroom else None,
    )
    _add_check(
        checks,
        "graph_cache_access_contract_ok",
        graph_cache_audit.get("verdict") == "graph_cache_access_contract_ok" if graph_cache_audit else False,
        graph_cache_audit.get("failed_checks") if graph_cache_audit else None,
    )
    _add_check(checks, "report_verdict_metric_sourced", _report_verdict_sourced(report_text, manifest))
    _add_check(checks, "git_status_readback_recorded", isinstance(manifest.get("git_status_readback"), str))
    _add_check(checks, "source_hashes_exist", _source_hashes_exist(manifest), sorted(manifest.get("source_file_hashes", {})))
    if generator_enabled:
        _add_001c_checks(checks, manifest, events, generator_spec, family_summary, graph_saturation, candidate_hash_check)
    if manifest.get("task_id") == "ITL-DEV-BENCH-001D" or manifest.get("candidate_factorial_interactions_path"):
        _add_001d_checks(checks, run_dir, manifest)

    failed = [check for check in checks if not check["ok"]]
    result = {
        "producer_function": "itl_devbench.eval.audit.audit_manifest",
        "manifest_path": str(manifest_path),
        "checks": checks,
        "failed_checks": failed,
        "verdict": "audit_succeeded" if not failed else "audit_failed",
    }
    output_path = run_dir / "audit_report.json"
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    return result


def _add_check(checks: list[Dict[str, Any]], name: str, ok: bool, detail: Any = None) -> None:
    checks.append({"name": name, "ok": bool(ok), "detail": detail})


def _forbidden_claims_absent(report_text: str) -> bool:
    lowered = report_text.lower()
    return not any(term in lowered for term in FORBIDDEN_CLAIM_STRINGS)


def _candidate_traces_hide_state(events: list[Dict[str, Any]]) -> bool:
    for event in events:
        if event.get("agent_kind") == "candidate" and "hidden_state" in json.dumps(event).lower():
            return False
    return True


def _prediction_order_before_env_result(trace_path: Path) -> bool:
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        if line.find('"pre_action_prediction"') == -1:
            return False
        if line.find('"pre_action_prediction"') > line.find('"env_result"'):
            return False
    return True


def _baseline_labels_valid(events: list[Dict[str, Any]]) -> bool:
    for event in events:
        if event["agent_id"] == "graph_cache" and event["agent_kind"] != "baseline":
            return False
        if event["agent_id"] == "oracle" and event["agent_kind"] != "oracle":
            return False
    return True


def _report_verdict_sourced(report_text: str, manifest: Dict[str, Any]) -> bool:
    verdict_line = next((line for line in report_text.splitlines() if line.startswith("Verdict: ")), "")
    verdict = verdict_line.replace("Verdict: ", "", 1)
    expected_sources = {
        "Verdict source: itl_devbench.eval.report.derive_report_verdict",
        "Verdict source: itl_devbench.eval.candidate_factorial.derive_candidate_factorial_verdict",
    }
    return (
        verdict in ALLOWED_VERDICTS
        and "Metric source: metrics.json" in report_text
        and "Replay source: replay_report.json" in report_text
        and any(source in report_text for source in expected_sources)
        and "Oracle headroom checks are stored in oracle_headroom_report.json." in report_text
        and "Graph-cache access audit is stored in leakage_audit_graph_cache.json." in report_text
        and verdict == manifest.get("report_verdict")
    )


def _source_hashes_exist(manifest: Dict[str, Any]) -> bool:
    source_hashes = manifest.get("source_file_hashes", {})
    normalized = {path.replace("\\", "/") for path in source_hashes}
    return all(required in normalized for required in REQUIRED_SOURCE_HASH_SUFFIXES)


def _resolve_path(run_dir: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else run_dir / path


def _read_json_if_exists(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _read_manifest_json(run_dir: Path, manifest: Dict[str, Any], key: str) -> Dict[str, Any]:
    value = manifest.get(key)
    if not value:
        return {}
    return _read_json_if_exists(_resolve_path(run_dir, str(value)))


def _add_001c_checks(
    checks: list[Dict[str, Any]],
    manifest: Dict[str, Any],
    events: list[Dict[str, Any]],
    generator_spec: Dict[str, Any],
    family_summary: Dict[str, Any],
    graph_saturation: Dict[str, Any],
    candidate_hash_check: Dict[str, Any],
) -> None:
    _add_check(checks, "generator_spec_001c_exists", bool(generator_spec))
    _add_check(checks, "heldout_split_no_overlap", not generator_spec.get("heldout_overlap_with_smoke"), generator_spec.get("heldout_overlap_with_smoke"))
    _add_check(
        checks,
        "candidate_source_hash_unchanged",
        candidate_hash_check.get("verdict") == "candidate_source_unchanged",
        candidate_hash_check,
    )
    required_artifact_keys = [
        "generator_spec_001c_path",
        "baseline_scores_by_family_path",
        "baseline_scores_by_dimension_path",
        "graph_cache_saturation_report_path",
        "family_metric_summary_path",
        "candidate_source_hash_check_path",
    ]
    _add_check(checks, "required_001c_artifact_paths_recorded", all(manifest.get(key) for key in required_artifact_keys))
    family_ids = {row.get("family_id") for row in family_summary.get("families", [])}
    _add_check(checks, "all_required_001c_families_present", set(REQUIRED_FAMILY_IDS).issubset(family_ids), sorted(family_ids))
    _add_check(
        checks,
        "oracle_headroom_valid_for_001c_families",
        all(row.get("valid_headroom") is True for row in family_summary.get("families", []))
        and set(REQUIRED_FAMILY_IDS).issubset(family_ids),
    )
    _add_check(
        checks,
        "graph_cache_scope_recorded",
        graph_saturation.get("graph_cache_cache_scope") in {"per_episode", "per_family", "per_split"},
        graph_saturation.get("graph_cache_cache_scope"),
    )
    _add_check(checks, "delayed_effect_trace_links_present", _delayed_effect_trace_links_present(events))
    _add_check(checks, "old_rule_return_sequence_present", _old_rule_return_sequence_present(events))
    _add_check(checks, "active_experiment_scored", _active_experiment_scored(events))


def _delayed_effect_trace_links_present(events: list[Dict[str, Any]]) -> bool:
    for event in events:
        if event.get("family_id") != "delayed_poison_v1":
            continue
        info = event["env_result"]["info"]
        if (
            info.get("delayed_effect_event_id") is not None
            and info.get("cause_event_id") is not None
            and int(info.get("delay_ticks") or 0) >= 7
            and info.get("source_object_id")
        ):
            return True
    return False


def _old_rule_return_sequence_present(events: list[Dict[str, Any]]) -> bool:
    phases = {
        str(event["env_result"]["info"].get("rule_phase"))
        for event in events
        if event.get("family_id") == "rule_reversal_return_v1"
    }
    return {"A", "B", "C", "A_prime"}.issubset(phases)


def _active_experiment_scored(events: list[Dict[str, Any]]) -> bool:
    return any(
        event.get("family_id") == "info_risk_tradeoff_v1"
        and event.get("A_t") in {"inspect", "sample_small_bite"}
        and float(event["env_result"]["info"].get("information_gain") or 0.0) > 0.0
        for event in events
    )


def _add_001d_checks(checks: list[Dict[str, Any]], run_dir: Path, manifest: Dict[str, Any]) -> None:
    scores = _read_manifest_json(run_dir, manifest, "candidate_factorial_scores_by_family_path")
    interactions = _read_manifest_json(run_dir, manifest, "candidate_factorial_interactions_path")
    baseline_comparison = _read_manifest_json(run_dir, manifest, "baseline_comparison_by_family_path")
    source_check = _read_manifest_json(run_dir, manifest, "source_hash_check_001d_path")
    required_artifact_keys = [
        "candidate_factorial_scores_by_family_path",
        "candidate_factorial_interactions_path",
        "baseline_comparison_by_family_path",
        "source_hash_check_001d_path",
    ]
    _add_check(checks, "required_001d_artifact_paths_recorded", all(manifest.get(key) for key in required_artifact_keys))
    _add_check(
        checks,
        "candidate_factorial_all_variants_present",
        scores.get("aggregate", {}).get("all_required_variants_present") is True,
        scores.get("aggregate"),
    )
    _add_check(
        checks,
        "candidate_factorial_interactions_computed",
        _interactions_have_required_fields(interactions),
        interactions.get("aggregate"),
    )
    _add_check(
        checks,
        "candidate_factorial_baseline_comparison_computed",
        bool(baseline_comparison.get("families")) and "baseline_saturated" in baseline_comparison.get("aggregate", {}),
        baseline_comparison.get("aggregate"),
    )
    _add_check(
        checks,
        "candidate_factorial_protected_sources_unchanged",
        source_check.get("candidate_source_unchanged") is True
        and source_check.get("protected_sources_unchanged") is True,
        source_check.get("protected_sources"),
    )


def _interactions_have_required_fields(interactions: Dict[str, Any]) -> bool:
    required = {
        "pe_marginal_under_memory_planning",
        "memory_marginal_under_pe_planning",
        "planner_read_marginal_under_pe_memory",
        "three_way_closure_gain",
    }
    by_family = interactions.get("by_family", [])
    if not by_family:
        return False
    if not all(required.issubset(row) for row in by_family):
        return False
    aggregate = interactions.get("aggregate", {})
    return all(f"{name}_mean" in aggregate for name in required)


def _headroom_valid_or_explicit_invalid(oracle_headroom: Dict[str, Any], manifest: Dict[str, Any]) -> bool:
    if not oracle_headroom:
        return False
    if oracle_headroom.get("aggregate", {}).get("oracle_upper_bound_valid") is True:
        return True
    return manifest.get("report_verdict") in {
        "oracle_headroom_unresolved",
        "benchmark_objective_contract_invalid",
        "oracle_no_headroom_benchmark_invalid",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True)
    args = parser.parse_args(argv)
    result = audit_manifest(args.manifest)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["verdict"] == "audit_succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main())
