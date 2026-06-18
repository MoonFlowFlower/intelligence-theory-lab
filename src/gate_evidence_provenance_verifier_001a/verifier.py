from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from .schema import (
    BASELINE_PROVENANCE_FIELDS,
    CHECKS,
    CLAIM_CEILING,
    REQUIRED_BUNDLE_FILES,
    REQUIRED_COMPUTED_GATE_INPUTS,
    STRONGEST_BASELINE_FIELDS,
    TASK_ID,
    VALID_VERDICT,
)


class BundleParseError(ValueError):
    pass


def _json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - exact decoder text is platform-specific
        raise BundleParseError(f"{path.name}: {type(exc).__name__}: {exc}") from exc


def _jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if not isinstance(row, dict):
                raise BundleParseError(f"{path.name}:{line_number}: row is not an object")
            rows.append(row)
    except BundleParseError:
        raise
    except Exception as exc:  # pragma: no cover - exact decoder text is platform-specific
        raise BundleParseError(f"{path.name}: {type(exc).__name__}: {exc}") from exc
    return rows


def _load_bundle(bundle_dir: Path) -> dict[str, Any]:
    if not bundle_dir.exists() or not bundle_dir.is_dir():
        raise BundleParseError(f"bundle directory not found: {bundle_dir}")
    missing = [name for name in REQUIRED_BUNDLE_FILES if not (bundle_dir / name).is_file()]
    if missing:
        raise BundleParseError("missing required files: " + ", ".join(missing))

    result = _json(bundle_dir / "result.json")
    baseline = _json(bundle_dir / "baseline_comparison.json")
    leakage = _json(bundle_dir / "leakage_scan.json")
    replay = _json(bundle_dir / "replay_report.json")
    source_pin = _json(bundle_dir / "source_pin_readback_report.json")
    rows = _jsonl(bundle_dir / "provenance_rows.jsonl")

    objects = {
        "result": result,
        "baseline": baseline,
        "leakage": leakage,
        "replay": replay,
        "source_pin": source_pin,
    }
    non_objects = [name for name, payload in objects.items() if not isinstance(payload, dict)]
    if non_objects:
        raise BundleParseError("non-object JSON payloads: " + ", ".join(non_objects))
    return {**objects, "rows": rows}


def _failure(check: str, reason: str) -> dict[str, str]:
    return {"check": check, "reason": reason}


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_hash(value: Any) -> bool:
    if not isinstance(value, str) or len(value) != 64:
        return False
    try:
        bytes.fromhex(value)
    except ValueError:
        return False
    return True


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _as_string_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str) and item}


def _baseline_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("kind") == "baseline_invocation"]


def _control_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if row.get("kind") == "control" and row.get("computed") is True]


def _valid_provenance_row(row: dict[str, Any]) -> bool:
    for field in BASELINE_PROVENANCE_FIELDS:
        if field not in row:
            return False
    if not _is_non_empty_string(row.get("producer_function")):
        return False
    if not isinstance(row.get("inputs"), list) or not row["inputs"]:
        return False
    if not _is_non_empty_string(row.get("run_id")):
        return False
    if not _is_non_empty_string(row.get("aggregation")):
        return False
    if not _is_hash(row.get("code_path_hash")):
        return False
    return True


def _consumption(result: dict[str, Any], key: str) -> set[str]:
    derivation = result.get("verdict_derivation")
    if not isinstance(derivation, dict):
        return set()
    return _as_string_set(derivation.get(key))


def _check_verdict_derivation(bundle: dict[str, Any]) -> dict[str, str] | None:
    result = bundle["result"]
    gate_inputs = result.get("computed_gate_inputs")
    derivation = result.get("verdict_derivation")
    if not isinstance(gate_inputs, dict) or not isinstance(derivation, dict):
        return _failure("verdict_derivation", "final verdict is detached from computed gate inputs")

    for key in REQUIRED_COMPUTED_GATE_INPUTS:
        if not isinstance(gate_inputs.get(key), bool):
            return _failure("verdict_derivation", f"computed gate input is missing or non-bool: {key}")

    derived = (
        "bundle_provenance_inputs_wellformed"
        if all(gate_inputs[key] for key in REQUIRED_COMPUTED_GATE_INPUTS)
        else "bundle_provenance_inputs_blocked"
    )
    if result.get("final_verdict") != derived:
        return _failure("verdict_derivation", "computed gate inputs do not reproduce final verdict")
    if derivation.get("terminal_reason_source") != "computed_gate_inputs":
        return _failure("verdict_derivation", "terminal reason is not derived from gate inputs")
    if not _is_non_empty_string(derivation.get("producer_function")):
        return _failure("verdict_derivation", "missing verdict producer function")
    if not isinstance(derivation.get("input_artifacts"), list) or not derivation["input_artifacts"]:
        return _failure("verdict_derivation", "missing verdict input artifact list")
    if not _is_non_empty_string(derivation.get("aggregation")):
        return _failure("verdict_derivation", "missing verdict aggregation")
    return None


def _check_baseline_invocation(bundle: dict[str, Any]) -> dict[str, str] | None:
    baseline = bundle["baseline"]
    rows = _baseline_rows(bundle["rows"])
    by_id = {row.get("baseline_id"): row for row in rows if _is_non_empty_string(row.get("baseline_id"))}
    listed = _as_string_set(baseline.get("listed_baseline_ids"))
    required = _as_string_set(baseline.get("required_baseline_ids")) or listed
    if not listed or not required:
        return _failure("baseline_invocation", "no listed or required baselines were recorded")

    missing_rows = sorted(baseline_id for baseline_id in listed | required if baseline_id not in by_id)
    if missing_rows:
        return _failure(
            "baseline_invocation",
            "baseline names are listed without provenance rows: " + ", ".join(missing_rows),
        )

    for baseline_id in sorted(required):
        row = by_id[baseline_id]
        if row.get("invoked") is not True:
            return _failure("baseline_invocation", f"baseline row was not invoked: {baseline_id}")
        if not _valid_provenance_row(row):
            return _failure(
                "baseline_invocation",
                f"baseline row lacks required callable provenance fields: {baseline_id}",
            )
    return None


def _check_strongest_baseline(bundle: dict[str, Any]) -> dict[str, str] | None:
    baseline = bundle["baseline"]
    rows = _baseline_rows(bundle["rows"])
    by_id = {row.get("baseline_id"): row for row in rows if _is_non_empty_string(row.get("baseline_id"))}

    for field in STRONGEST_BASELINE_FIELDS:
        if field not in baseline:
            return _failure("strongest_baseline_coverage", f"missing strongest-baseline field: {field}")
    if "equivalence_band" not in baseline and "margin_threshold" not in baseline:
        return _failure("strongest_baseline_coverage", "missing equivalence band or margin threshold")
    if not _is_number(baseline.get("candidate_score")):
        return _failure("strongest_baseline_coverage", "candidate score is not numeric")
    if not _is_number(baseline.get("strongest_fair_baseline_score")):
        return _failure("strongest_baseline_coverage", "strongest fair baseline score is not numeric")
    if not _is_number(baseline.get("delta_vs_strongest_fair")):
        return _failure("strongest_baseline_coverage", "delta vs strongest fair is not numeric")
    threshold = baseline.get("equivalence_band", baseline.get("margin_threshold"))
    if not _is_number(threshold):
        return _failure("strongest_baseline_coverage", "equivalence threshold is not numeric")

    strongest_id = baseline.get("strongest_fair_baseline_id")
    if not _is_non_empty_string(strongest_id):
        return _failure("strongest_baseline_coverage", "strongest fair baseline id is missing")
    strongest_row = by_id.get(strongest_id)
    if strongest_row is None or strongest_row.get("invoked") is not True:
        return _failure("strongest_baseline_coverage", "strongest fair baseline was not computed")
    if not _valid_provenance_row(strongest_row):
        return _failure("strongest_baseline_coverage", "strongest fair baseline row is not tied to provenance")
    if baseline.get("strongest_fair_consumed_by_final_verdict") is not True:
        return _failure("strongest_baseline_coverage", "strongest fair baseline was not consumed")
    if strongest_id not in _consumption(bundle["result"], "consumed_baseline_ids"):
        return _failure("strongest_baseline_coverage", "strongest fair baseline not tied to verdict derivation")
    return None


def _check_leakage(bundle: dict[str, Any]) -> dict[str, str] | None:
    leakage = bundle["leakage"]
    scanner = leakage.get("scanner")
    if not isinstance(scanner, dict) or not _valid_provenance_row(scanner):
        return _failure("leakage_positive_control", "leakage scanner provenance is absent or incomplete")
    controls = leakage.get("positive_controls")
    if not isinstance(controls, list) or not controls:
        return _failure("leakage_positive_control", "no leakage positive-control case exists")
    consumed = _consumption(bundle["result"], "consumed_leakage_positive_control_ids")
    for control in controls:
        if not isinstance(control, dict):
            return _failure("leakage_positive_control", "leakage positive-control row is malformed")
        case_id = control.get("case_id")
        if not _is_non_empty_string(case_id):
            return _failure("leakage_positive_control", "leakage positive-control case id is missing")
        if control.get("same_admission_path") is not True:
            return _failure("leakage_positive_control", "leakage positive-control did not use admission path")
        if control.get("detected") is not True:
            return _failure("leakage_positive_control", "leakage positive-control was not detected")
        if control.get("consumed_by_final_verdict") is not True or case_id not in consumed:
            return _failure("leakage_positive_control", "leakage positive-control was not consumed")
        if control.get("failure_recorded") is True and control.get("consumed_by_final_verdict") is not True:
            return _failure("leakage_positive_control", "leakage positive-control failure was ignored")
    return None


def _check_replay(bundle: dict[str, Any]) -> dict[str, str] | None:
    replay = bundle["replay"]
    stored_only_flags = (
        "hash_only",
        "stored_hashes_only",
        "stored_actions_only",
        "stored_verdicts_only",
        "stored_scores_only",
    )
    if any(replay.get(flag) is True for flag in stored_only_flags):
        return _failure("replay_recompute", "replay evidence only compared stored artifacts")
    required_true = (
        "recomputed_from_serialized_state",
        "recomputed_from_observation",
        "candidate_behavior_recomputed",
        "baseline_behavior_recomputed",
        "score_recomputed",
    )
    for field in required_true:
        if replay.get(field) is not True:
            return _failure("replay_recompute", f"replay did not recompute required behavior: {field}")
    if replay.get("mode") != "recompute_from_serialized_state_and_observation":
        return _failure("replay_recompute", "replay mode is not serialized-state recompute")
    return None


def _check_source_pin(bundle: dict[str, Any]) -> dict[str, str] | None:
    source_pin = bundle["source_pin"]
    if source_pin.get("self_comparison_only") is True:
        return _failure("source_pin_readback", "source pin compares only to itself")
    channels = source_pin.get("readback_channels")
    if not isinstance(channels, list):
        return _failure("source_pin_readback", "source readback channels are missing")
    authoritative = [
        channel
        for channel in channels
        if isinstance(channel, dict)
        and channel.get("authoritative") is True
        and _is_non_empty_string(channel.get("channel"))
        and _is_hash(channel.get("sha256"))
    ]
    if len({channel["channel"] for channel in authoritative}) < 2:
        return _failure("source_pin_readback", "source readback lacks two authoritative channels")
    conflicts = source_pin.get("conflicts", [])
    if not isinstance(conflicts, list):
        return _failure("source_pin_readback", "source readback conflict list is malformed")
    if conflicts and source_pin.get("fail_closed_on_conflict") is not True:
        return _failure("source_pin_readback", "source readback conflict does not fail closed")
    if any(isinstance(conflict, dict) and conflict.get("resolved") is not True for conflict in conflicts):
        return _failure("source_pin_readback", "source readback conflict is unresolved")
    control = source_pin.get("truncation_positive_control")
    if isinstance(control, dict):
        case_id = control.get("case_id")
        consumed = _consumption(bundle["result"], "consumed_source_pin_control_ids")
        if not _is_non_empty_string(case_id):
            return _failure("source_pin_readback", "source truncation control case id is missing")
        if control.get("detected") is not True:
            return _failure("source_pin_readback", "source truncation positive-control was not detected")
        if control.get("consumed_by_final_verdict") is not True or case_id not in consumed:
            return _failure("source_pin_readback", "source truncation positive-control was not consumed")
    return None


def _check_control_consumption(bundle: dict[str, Any]) -> dict[str, str] | None:
    consumed_controls = _consumption(bundle["result"], "consumed_control_ids")
    for row in _control_rows(bundle["rows"]):
        control_id = row.get("control_id")
        if not _is_non_empty_string(control_id):
            return _failure("control_consumption", "computed control row lacks control id")
        if control_id not in consumed_controls:
            return _failure("control_consumption", f"computed control was not consumed: {control_id}")
        if "consumed_by_final_verdict" in row and row.get("consumed_by_final_verdict") is not True:
            return _failure("control_consumption", f"computed control explicitly not consumed: {control_id}")
    return None


CHECK_TO_VERDICT = {
    "verdict_derivation": "invalid_literal_or_detached_verdict",
    "baseline_invocation": "invalid_missing_or_uninvoked_baseline",
    "strongest_baseline_coverage": "invalid_missing_strongest_baseline",
    "leakage_positive_control": "invalid_leakage_positive_control_absent_or_not_consumed",
    "replay_recompute": "invalid_replay_not_recomputed",
    "source_pin_readback": "invalid_source_pin_self_readback_or_conflict",
    "control_consumption": "invalid_control_computed_but_not_consumed",
}


CHECK_FUNCTIONS = (
    ("verdict_derivation", _check_verdict_derivation),
    ("baseline_invocation", _check_baseline_invocation),
    ("strongest_baseline_coverage", _check_strongest_baseline),
    ("leakage_positive_control", _check_leakage),
    ("replay_recompute", _check_replay),
    ("source_pin_readback", _check_source_pin),
    ("control_consumption", _check_control_consumption),
)


def _result(
    bundle_dir: Path,
    verdict: str,
    checks_run: list[str],
    failed_checks: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "task_id": TASK_ID,
        "verdict": verdict,
        "bundle_dir": str(bundle_dir),
        "checks_run": checks_run,
        "failed_checks": failed_checks,
        "claim_ceiling": CLAIM_CEILING,
        "no_gate_pass_claim": True,
    }


def verify_bundle(bundle_dir: str | Path) -> dict[str, Any]:
    bundle_path = Path(bundle_dir)
    checks_run = ["schema_parse"]
    try:
        bundle = _load_bundle(bundle_path)
    except BundleParseError as exc:
        return _result(
            bundle_path,
            "invalid_schema_or_parse_failure",
            checks_run,
            [_failure("schema_parse", str(exc))],
        )

    failed_checks: list[dict[str, str]] = []
    for check_name, check_function in CHECK_FUNCTIONS:
        checks_run.append(check_name)
        failure = check_function(bundle)
        if failure is None:
            continue
        failed_checks.append(failure)
        return _result(bundle_path, CHECK_TO_VERDICT[check_name], checks_run, failed_checks)
    return _result(bundle_path, VALID_VERDICT, checks_run, failed_checks)


def _base_fixture() -> dict[str, Any]:
    hash_a = "a" * 64
    hash_b = "b" * 64
    hash_c = "c" * 64
    hash_d = "d" * 64
    hash_e = "e" * 64
    return {
        "result.json": {
            "schema_version": "gate_evidence_provenance_verifier_001a_fixture_v1",
            "final_verdict": "bundle_provenance_inputs_wellformed",
            "expected_verdict": "invalid_literal_or_detached_verdict",
            "computed_gate_inputs": {
                "baseline_invocation": True,
                "strongest_baseline": True,
                "leakage_positive_control": True,
                "replay_recompute": True,
                "source_pin_readback": True,
                "control_consumption": True,
            },
            "verdict_derivation": {
                "producer_function": "synthetic_verdicts.select_decision_verdict",
                "input_artifacts": [
                    "baseline_comparison.json",
                    "provenance_rows.jsonl",
                    "leakage_scan.json",
                    "replay_report.json",
                    "source_pin_readback_report.json",
                ],
                "aggregation": "all_required_gates_true_fail_closed",
                "terminal_reason_source": "computed_gate_inputs",
                "terminal_reason_id": "all_required_gates_true",
                "consumed_baseline_ids": ["graph_cache_collapse"],
                "consumed_control_ids": ["full_budget_saturation", "baseline_saturation"],
                "consumed_leakage_positive_control_ids": ["leakage-pc-label"],
                "consumed_source_pin_control_ids": ["source-truncation-pc"],
            },
        },
        "baseline_comparison.json": {
            "candidate_score": 0.72,
            "listed_baseline_ids": ["graph_cache_collapse"],
            "required_baseline_ids": ["graph_cache_collapse"],
            "strongest_fair_baseline_id": "graph_cache_collapse",
            "strongest_fair_baseline_score": 0.71,
            "delta_vs_strongest_fair": 0.01,
            "equivalence_band": 0.02,
            "strongest_fair_consumed_by_final_verdict": True,
        },
        "provenance_rows.jsonl": [
            {
                "row_id": "prov-baseline-graph-cache",
                "kind": "baseline_invocation",
                "baseline_id": "graph_cache_collapse",
                "invoked": True,
                "producer_function": "synthetic_baselines.graph_cache_collapse",
                "inputs": ["candidate_trace.jsonl"],
                "run_id": "run-baseline-001",
                "aggregation": "mean(score)",
                "code_path_hash": hash_a,
            },
            {
                "row_id": "control-full-budget",
                "kind": "control",
                "control_id": "full_budget_saturation",
                "computed": True,
                "producer_function": "synthetic_controls.full_budget_saturation",
                "inputs": ["result.json"],
                "run_id": "run-control-001",
                "aggregation": "fail_closed_if_saturated",
                "code_path_hash": hash_b,
            },
            {
                "row_id": "control-baseline-saturation",
                "kind": "control",
                "control_id": "baseline_saturation",
                "computed": True,
                "producer_function": "synthetic_controls.baseline_saturation",
                "inputs": ["baseline_comparison.json"],
                "run_id": "run-control-002",
                "aggregation": "fail_closed_if_saturated",
                "code_path_hash": hash_c,
            },
        ],
        "leakage_scan.json": {
            "scanner": {
                "producer_function": "synthetic_leakage.scan",
                "inputs": ["candidate_trace.jsonl"],
                "run_id": "run-leakage-001",
                "aggregation": "any_detected",
                "code_path_hash": hash_d,
            },
            "positive_controls": [
                {
                    "case_id": "leakage-pc-label",
                    "same_admission_path": True,
                    "detected": True,
                    "failure_recorded": False,
                    "consumed_by_final_verdict": True,
                }
            ],
        },
        "replay_report.json": {
            "mode": "recompute_from_serialized_state_and_observation",
            "recomputed_from_serialized_state": True,
            "recomputed_from_observation": True,
            "candidate_behavior_recomputed": True,
            "baseline_behavior_recomputed": True,
            "score_recomputed": True,
            "hash_only": False,
            "stored_hashes_only": False,
            "stored_actions_only": False,
            "stored_verdicts_only": False,
            "stored_scores_only": False,
        },
        "source_pin_readback_report.json": {
            "self_comparison_only": False,
            "readback_channels": [
                {
                    "channel": "git_blob",
                    "authoritative": True,
                    "source_path": "src/synthetic.py",
                    "sha256": hash_e,
                },
                {
                    "channel": "filesystem_readback",
                    "authoritative": True,
                    "source_path": "src/synthetic.py",
                    "sha256": hash_e,
                },
            ],
            "conflicts": [],
            "fail_closed_on_conflict": True,
            "truncation_positive_control": {
                "case_id": "source-truncation-pc",
                "detected": True,
                "consumed_by_final_verdict": True,
            },
        },
    }


def _mutate_literal_verdict(bundle: dict[str, Any]) -> None:
    bundle["result.json"].pop("computed_gate_inputs")
    bundle["result.json"]["verdict_derivation"] = {
        "terminal_reason_source": "literal",
        "terminal_reason_id": "looks_green",
    }


def _mutate_missing_baseline(bundle: dict[str, Any]) -> None:
    bundle["provenance_rows.jsonl"] = [
        row for row in bundle["provenance_rows.jsonl"] if row.get("kind") != "baseline_invocation"
    ]


def _mutate_missing_strongest(bundle: dict[str, Any]) -> None:
    bundle["baseline_comparison.json"].pop("strongest_fair_baseline_id")
    bundle["baseline_comparison.json"].pop("strongest_fair_baseline_score")
    bundle["baseline_comparison.json"].pop("delta_vs_strongest_fair")


def _mutate_no_leakage_positive(bundle: dict[str, Any]) -> None:
    bundle["leakage_scan.json"]["positive_controls"] = []


def _mutate_hash_only_replay(bundle: dict[str, Any]) -> None:
    bundle["replay_report.json"].update(
        {
            "mode": "stored_hash_compare",
            "recomputed_from_serialized_state": False,
            "recomputed_from_observation": False,
            "candidate_behavior_recomputed": False,
            "baseline_behavior_recomputed": False,
            "score_recomputed": False,
            "hash_only": True,
            "stored_hashes_only": True,
        }
    )


def _mutate_source_self_readback(bundle: dict[str, Any]) -> None:
    bundle["source_pin_readback_report.json"]["self_comparison_only"] = True
    bundle["source_pin_readback_report.json"]["readback_channels"] = [
        bundle["source_pin_readback_report.json"]["readback_channels"][0]
    ]


def _mutate_control_not_consumed(bundle: dict[str, Any]) -> None:
    bundle["provenance_rows.jsonl"].append(
        {
            "row_id": "control-orphan-full-budget",
            "kind": "control",
            "control_id": "orphan_full_budget_saturation",
            "computed": True,
            "producer_function": "synthetic_controls.orphan_full_budget",
            "inputs": ["result.json"],
            "run_id": "run-control-orphan",
            "aggregation": "fail_closed_if_saturated",
            "code_path_hash": "a" * 64,
        }
    )


FIXTURE_MUTATORS = {
    "valid_minimal_bundle": (None, VALID_VERDICT),
    "literal_verdict_bundle": (_mutate_literal_verdict, "invalid_literal_or_detached_verdict"),
    "missing_baseline_invocation_bundle": (
        _mutate_missing_baseline,
        "invalid_missing_or_uninvoked_baseline",
    ),
    "missing_strongest_baseline_bundle": (
        _mutate_missing_strongest,
        "invalid_missing_strongest_baseline",
    ),
    "leakage_positive_control_absent_bundle": (
        _mutate_no_leakage_positive,
        "invalid_leakage_positive_control_absent_or_not_consumed",
    ),
    "hash_only_replay_bundle": (_mutate_hash_only_replay, "invalid_replay_not_recomputed"),
    "source_pin_self_readback_bundle": (
        _mutate_source_self_readback,
        "invalid_source_pin_self_readback_or_conflict",
    ),
    "control_not_consumed_bundle": (
        _mutate_control_not_consumed,
        "invalid_control_computed_but_not_consumed",
    ),
}


def _write_bundle_files(bundle_dir: Path, payloads: dict[str, Any]) -> None:
    bundle_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in payloads.items():
        path = bundle_dir / name
        if name.endswith(".jsonl"):
            path.write_text(
                "".join(json.dumps(row, sort_keys=True) + "\n" for row in payload),
                encoding="utf-8",
            )
            continue
        path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def write_synthetic_fixtures(root: str | Path) -> dict[str, Any]:
    root_path = Path(root)
    root_path.mkdir(parents=True, exist_ok=True)
    manifest: dict[str, Any] = {"task_id": TASK_ID, "fixtures": []}
    for fixture_name, (mutator, expected_verdict) in FIXTURE_MUTATORS.items():
        payload = copy.deepcopy(_base_fixture())
        if mutator is not None:
            mutator(payload)
        fixture_dir = root_path / fixture_name
        _write_bundle_files(fixture_dir, payload)
        manifest["fixtures"].append(
            {
                "fixture_name": fixture_name,
                "bundle_dir": str(fixture_dir),
                "expected_verdict": expected_verdict,
                "expected_verdict_literal_ignored": True,
            }
        )
    return manifest
