"""Callable S3b artifact producers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import time
from typing import Any, Iterable, Mapping

from .battery.graph_cache import (
    GRAPH_CACHE_CLASSES,
    GRAPH_CACHE_MEMBER_NAMES,
    build_graph_cache_alias_report,
    fitting_data_contract,
    graph_cache_code_hash,
    graph_cache_conventions,
)
from .battery.base import event_from_mapping
from .battery.rag_nn import RETRIEVAL_MEMBER_NAMES, retrieval_code_hash, retrieval_conventions
from .leak_scan import LIMITATION_TEXT, _scan_payload
from .trajectory_sets import TrajectorySetSpec, _canonical_line, _iter_records_with_adjudicator, load_frozen_design


def write_materialized_leak_scan_report(
    frozen_design_path: str | Path,
    trajectory_manifest_path: str | Path,
    output_path: str | Path,
) -> dict[str, Any]:
    run_started_at = _utc_timestamp()
    start = time.perf_counter()
    design = load_frozen_design(frozen_design_path)
    manifest = _read_json(trajectory_manifest_path)
    set_reports = []
    passed = True
    stop_condition = None
    for entry in manifest["sets"]:
        spec = _spec_from_entry(entry)
        regenerated_sha = _member_view_sha256(design, spec)
        set_report = {
            "set_id": str(entry["set_id"]),
            "records_scanned": 0,
            "member_view_record_count": int(entry["member_view_record_count"]),
            "expected_member_view_sha256": str(entry["member_view_sha256"]),
            "regenerated_member_view_sha256": regenerated_sha,
            "sha256_verified": regenerated_sha == str(entry["member_view_sha256"]),
            "findings": [],
        }
        if not set_report["sha256_verified"]:
            passed = False
            stop_condition = "member_view_sha256_mismatch"
            set_reports.append(set_report)
            break
        findings, count = _scan_spec_records(design, spec)
        set_report["records_scanned"] = count
        set_report["findings"] = findings
        if count != int(entry["member_view_record_count"]):
            passed = False
            stop_condition = "member_view_record_count_mismatch"
        if findings:
            passed = False
            stop_condition = stop_condition or "leak_scan_findings"
        set_reports.append(set_report)
        if stop_condition:
            break
    report = {
        "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
        "stage": "S3b",
        "artifact": "s3b_leak_scan_report",
        "passed": passed,
        "scanned_files": [],
        "sets": set_reports,
        "known_limitation": LIMITATION_TEXT,
        "claim": "key/type-based scan of regenerated in-memory member-view records only; not leak-proof",
        "trajectory_manifest_path": str(trajectory_manifest_path),
        "producer_function": "src.fsp_pum_env.s3b_artifacts.write_materialized_leak_scan_report",
        "input_artifacts": [str(frozen_design_path), str(trajectory_manifest_path)],
        "aggregation_rule": "pass iff every set sha matches, every set record count matches, and no key/type findings are emitted",
        "code_path_hash": _code_path_hash(),
        "run_id": f"s3b-leak-scan-{run_started_at}",
        "run_started_at": run_started_at,
        "run_finished_at": _utc_timestamp(),
        "wall_clock_seconds": time.perf_counter() - start,
        "claim_ceiling": "S3b leak-scan instrumentation only; planted value mutant remains S4",
    }
    if stop_condition is not None:
        report["stop_condition"] = stop_condition
    _write_json(output_path, report)
    return report


def write_s3b_battery_manifest(frozen_design_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    run_started_at = _utc_timestamp()
    start = time.perf_counter()
    design = load_frozen_design(frozen_design_path)
    members = GRAPH_CACHE_MEMBER_NAMES + RETRIEVAL_MEMBER_NAMES
    missing = [name for name in members if name not in design["battery_membership"]["members"]]
    if missing:
        raise ValueError(f"implemented S3b member missing from frozen battery_membership: {missing}")
    shared_contract = fitting_data_contract(design)
    manifest = {
        "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
        "stage": "S3b",
        "artifact": "s3b_battery_manifest",
        "implemented_members": members,
        "prediction_format": {
            "prediction_target": design["evaluation"]["prediction_target"],
            "response_alphabet_size": int(design["env_parameters"]["renderer"]["response_alphabet_size"]),
            "counterfactual_action_set_per_query": list(design["evaluation"]["counterfactual_action_set_per_query"]),
            "format": "mapping from counterfactual action name to a full probability distribution over the frozen response alphabet",
        },
        "fitting_data_contract": shared_contract,
        "fitting_data_contracts": {name: dict(shared_contract) for name in members},
        "graph_cache_conventions": graph_cache_conventions(),
        "retrieval_conventions": retrieval_conventions(),
        "not_in_s3b": ["gap scoring", "headroom numbers", "should-win certificates", "obs decoders", "sequence models"],
        "producer_function": "src.fsp_pum_env.s3b_artifacts.write_s3b_battery_manifest",
        "code_path_hash": _code_path_hash(),
        "component_code_hashes": {
            "graph_cache": graph_cache_code_hash(),
            "rag_nn": retrieval_code_hash(),
        },
        "run_id": f"s3b-battery-manifest-{run_started_at}",
        "run_started_at": run_started_at,
        "run_finished_at": _utc_timestamp(),
        "wall_clock_seconds": time.perf_counter() - start,
        "claim_ceiling": "S3b battery member conventions and fitting contracts only; no baseline-power or gap claim",
    }
    _write_json(output_path, manifest)
    return manifest


def write_graph_cache_alias_reports(
    frozen_design_path: str | Path,
    trajectory_manifest_path: str | Path,
    output_dir: str | Path,
) -> list[dict[str, Any]]:
    run_started_at = _utc_timestamp()
    design = load_frozen_design(frozen_design_path)
    manifest = _read_json(trajectory_manifest_path)
    predictors = {name: GRAPH_CACHE_CLASSES[name].from_design(design) for name in GRAPH_CACHE_MEMBER_NAMES}
    train_record_count = 0
    for record in _iter_partition_records(design, manifest["sets"], "train"):
        train_record_count += 1
        for predictor in predictors.values():
            predictor.observe(record)
    train_summaries = {}
    for name, predictor in predictors.items():
        train_summaries[name] = {
            "total_records": train_record_count,
            "total_keys": predictor.distinct_key_count,
            "keys_seen_in_fitted_table": predictor.distinct_key_count,
            "coverage_fraction": 1.0 if predictor.distinct_key_count else 0.0,
        }
    heldout_summaries = _summarize_all_key_coverage(
        predictors,
        _iter_partition_records(design, manifest["sets"], "heldout"),
    )
    reports = []
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, predictor in predictors.items():
        report = build_graph_cache_alias_report(name, predictor, [], [], design=design)
        report["train_key_coverage"] = train_summaries[name]
        report["heldout_key_coverage"] = heldout_summaries[name]
        report["run_id"] = f"s3b-alias-{name}-{run_started_at}"
        report["run_started_at"] = run_started_at
        report["run_finished_at"] = _utc_timestamp()
        report["code_path_hash"] = graph_cache_code_hash()
        _write_json(out_dir / f"s3b_alias_report_{name}.json", report)
        reports.append(report)
    return reports


def _summarize_all_key_coverage(
    predictors: Mapping[str, Any],
    records: Iterable[Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    prefixes = {name: [] for name in predictors}
    observed = {name: {} for name in predictors}
    total_records = 0
    for record in records:
        parsed = event_from_mapping(record)
        total_records += 1
        if parsed.step_index == 0:
            prefixes = {name: [] for name in predictors}
        for name, predictor in predictors.items():
            key = predictor.key_for_event(parsed, prefixes[name])
            observed[name][key] = observed[name].get(key, 0) + 1
            prefixes[name].append(parsed)
    summaries = {}
    for name, predictor in predictors.items():
        fitted_keys = set(predictor._table)
        keys = set(observed[name])
        covered = len(keys & fitted_keys)
        summaries[name] = {
            "total_records": total_records,
            "total_keys": len(keys),
            "keys_seen_in_fitted_table": covered,
            "coverage_fraction": (covered / len(keys)) if keys else 0.0,
        }
    return summaries


def _iter_partition_records(
    design: Mapping[str, Any],
    entries: Iterable[Mapping[str, Any]],
    partition_name: str,
):
    for entry in entries:
        spec = _spec_from_entry(entry, only_partition=partition_name)
        for _, _, member_record, _ in _iter_records_with_adjudicator(design, spec):
            yield member_record


def _member_view_sha256(design: Mapping[str, Any], spec: TrajectorySetSpec) -> str:
    h = hashlib.sha256()
    for partition, trajectory_ordinal, member_record, _ in _iter_records_with_adjudicator(design, spec):
        if int(member_record["step_index"]) == 0:
            h.update(f"trajectory\t{partition}\t{trajectory_ordinal}\n".encode("utf-8"))
        h.update(_canonical_line(member_record))
    return h.hexdigest()


def _scan_spec_records(design: Mapping[str, Any], spec: TrajectorySetSpec) -> tuple[list[dict[str, Any]], int]:
    findings: list[dict[str, Any]] = []
    count = 0
    for _, _, member_record, _ in _iter_records_with_adjudicator(design, spec):
        count += 1
        findings.extend(_scan_payload(member_record, file=f"in_memory:{spec.set_id}", json_path=f"$[{count}]"))
    return findings, count


def _spec_from_entry(entry: Mapping[str, Any], *, only_partition: str | None = None) -> TrajectorySetSpec:
    params = entry["generation_params"]
    source_partitions = params["partitions"]
    ordered_names = [name for name in ("train", "heldout") if name in source_partitions]
    ordered_names.extend(name for name in source_partitions if name not in ordered_names)
    partitions = {
        name: {
            "start_user_id": int(source_partitions[name]["start_user_id"]),
            "count": int(source_partitions[name]["count"]),
        }
        for name in ordered_names
    }
    if only_partition is not None:
        partitions = {only_partition: partitions[only_partition]}
    return TrajectorySetSpec(
        set_id=str(params["set_id"]),
        master_seed=int(params["master_seed"]),
        env_mode=str(params["env_mode"]),
        partitions=partitions,
        turns_per_user=int(params["turns_per_user"]),
        logging_policy=params["logging_policy"],
    )


def _read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _write_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _code_path_hash() -> str:
    h = hashlib.sha256()
    for path in (
        Path(__file__),
        Path(__file__).with_name("leak_scan.py"),
        Path(__file__).with_name("trajectory_sets.py"),
        Path(__file__).parent / "battery" / "graph_cache.py",
        Path(__file__).parent / "battery" / "rag_nn.py",
    ):
        h.update(path.name.encode("utf-8"))
        h.update(path.read_bytes())
    return h.hexdigest()


def _utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
