from __future__ import annotations

import hashlib
import importlib
import inspect
import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "EVIDENCE-ADMISSION-VERIFIER-001A"
CLAIM_CEILING = "standalone evidence-admission filtering for future citation only"
PRODUCER_SOURCE_PATH = "src/evidence_admission_verifier_001a/core.py"
AGGREGATION_RULE = "first blocking evidence-admission rule in fixed precedence order"
CALLABLE_RECOMPUTE_CONTRACT = "callable_result_digest_v1"
SUPPORTED_AGGREGATION_RULES = {CALLABLE_RECOMPUTE_CONTRACT}

REQUIRED_OUTPUTS = {
    "result.json",
    "admission_decision.json",
    "block_reason_matrix.json",
    "verified_provenance_rows.jsonl",
    "callable_provenance_checks.jsonl",
    "fixture_manifest.json",
    "claim_ceiling.txt",
}

METRIC_REQUIRED_FIELDS = {
    "metric_id",
    "metric_name",
    "evidence_role",
    "producer_function",
    "producer_module",
    "code_path_hash",
    "run_id",
    "episode_ids",
    "seed_ids",
    "train_context_ids_consumed",
    "heldout_context_ids_consumed",
    "counterfactual_pair_ids_consumed",
    "input_artifact_paths",
    "input_artifact_hashes",
    "input_row_count",
    "output_artifact_path",
    "output_row_ids",
    "aggregation_rule",
    "threshold_used",
    "threshold_frozen_before_run",
    "computed_not_literal",
    "failure_path_available",
}

FORBIDDEN_CLAIM_TERMS = {
    "mechanism validity",
    "gate4 validity",
    "ego readiness",
    "runtime readiness",
    "bridge readiness",
    "companion readiness",
    "consciousness",
    "subjective experience",
    "real emotion",
    "self-awareness",
    "autonomy",
    "stable user benefit",
    "agency success",
}

PASS_SHAPED_TERMS = {
    "pass",
    "passed",
    "admitted_for_citation",
    "ready",
    "green",
    "bounded_pass",
}

DECISION_PRECEDENCE = [
    "blocked_fake_pass",
    "blocked_missing_callable_provenance",
    "blocked_callable_provenance_mismatch",
    "blocked_missing_baseline",
    "blocked_missing_ablation_rerun",
    "blocked_missing_leakage_positive_control",
    "blocked_missing_replay_recompute",
    "blocked_claim_inflation",
]


def _now_run_id() -> str:
    return "evidence_admission_verifier_001a_" + datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _source_hash() -> str:
    return _sha256_bytes(Path(__file__).read_bytes())


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _verifier_source_hashes() -> dict[str, str]:
    root = _repo_root()
    paths = [
        root / "src" / "evidence_admission_verifier_001a" / "__init__.py",
        root / "src" / "evidence_admission_verifier_001a" / "__main__.py",
        root / "src" / "evidence_admission_verifier_001a" / "core.py",
    ]
    return {
        path.relative_to(root).as_posix(): _sha256_bytes(path.read_bytes())
        for path in paths
        if path.exists()
    }


def _json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=True, default=_json_default)
        + "\n",
        encoding="utf-8",
    )


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text(
        "".join(json.dumps(row, sort_keys=True, ensure_ascii=True) + "\n" for row in rows),
        encoding="utf-8",
    )


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[Any]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _load_bundle(bundle_path: Path) -> dict[str, Any]:
    bundle_path = Path(bundle_path)
    if not bundle_path.exists() or not bundle_path.is_dir():
        raise FileNotFoundError(f"Evidence bundle directory not found: {bundle_path}")

    json_payloads: dict[str, Any] = {}
    jsonl_rows: dict[str, list[Any]] = {}
    text_payloads: dict[str, str] = {}
    input_records: list[dict[str, Any]] = []

    for path in sorted(item for item in bundle_path.rglob("*") if item.is_file()):
        rel = path.relative_to(bundle_path).as_posix()
        raw = path.read_bytes()
        record = {
            "path": rel,
            "sha256": _sha256_bytes(raw),
            "size_bytes": len(raw),
            "kind": "bytes",
        }
        if path.suffix.lower() == ".json":
            payload = _read_json(path)
            json_payloads[rel] = payload
            record["kind"] = "json"
        elif path.suffix.lower() == ".jsonl":
            rows = _read_jsonl(path)
            jsonl_rows[rel] = rows
            record["kind"] = "jsonl"
            record["row_count"] = len(rows)
        elif path.suffix.lower() in {".txt", ".md"}:
            text_payloads[rel] = path.read_text(encoding="utf-8")
            record["kind"] = "text"
        input_records.append(record)

    return {
        "bundle_path": bundle_path,
        "json_payloads": json_payloads,
        "jsonl_rows": jsonl_rows,
        "text_payloads": text_payloads,
        "input_records": input_records,
    }


def _rows_named(bundle: dict[str, Any], filename: str) -> list[dict[str, Any]]:
    rows = []
    for path, values in bundle["jsonl_rows"].items():
        if Path(path).name == filename:
            rows.extend(row for row in values if isinstance(row, dict))
    return rows


def _json_named(bundle: dict[str, Any], filename: str) -> list[dict[str, Any]]:
    payloads = []
    for path, payload in bundle["json_payloads"].items():
        if Path(path).name == filename and isinstance(payload, dict):
            payloads.append(payload)
    return payloads


def _all_text(bundle: dict[str, Any]) -> str:
    chunks: list[str] = []
    for payload in bundle["json_payloads"].values():
        chunks.append(json.dumps(payload, sort_keys=True, ensure_ascii=True))
    chunks.extend(bundle["text_payloads"].values())
    return "\n".join(chunks).casefold()


def _claim_text(bundle: dict[str, Any]) -> str:
    chunks = []
    for path, text in bundle["text_payloads"].items():
        if Path(path).name in {"claim_ceiling.txt", "report.md"}:
            chunks.append(text)
    return "\n".join(chunks).casefold()


def _has_pass_shaped_text(bundle: dict[str, Any]) -> bool:
    text = _all_text(bundle)
    return any(term in text for term in PASS_SHAPED_TERMS)


def _has_claim_inflation(bundle: dict[str, Any]) -> bool:
    text = _claim_text(bundle)
    for line in text.splitlines():
        normalized = " ".join(line.casefold().split())
        for term in FORBIDDEN_CLAIM_TERMS:
            if term not in normalized:
                continue
            negated_forms = (
                f"no {term}",
                f"not {term}",
                f"does not prove {term}",
                f"does not authorize {term}",
                f"cannot prove {term}",
                f"without {term}",
            )
            if any(form in normalized for form in negated_forms):
                continue
            return True
    return False


def _reason(
    reason_id: str,
    decision: str,
    source: str,
    evidence_path: str,
    detail: str,
) -> dict[str, Any]:
    return {
        "reason_id": reason_id,
        "canonical_decision": decision,
        "source": source,
        "evidence_path": evidence_path,
        "detail": detail,
        "computed": True,
        "verdict_text_used": False,
    }


def _normalize_sha256(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().casefold()
    if normalized.startswith("sha256:"):
        normalized = normalized.removeprefix("sha256:")
    if len(normalized) != 64:
        return None
    try:
        bytes.fromhex(normalized)
    except ValueError:
        return None
    return normalized


def _import_callable(producer: Any) -> tuple[Any | None, dict[str, Any]]:
    details: dict[str, Any] = {
        "producer_function": producer,
        "resolved_source_file_path": None,
        "resolved_code_hash": None,
        "import_error": None,
    }
    if not isinstance(producer, str) or ":" not in producer:
        details["error_reason_id"] = "unsupported_producer_function_format"
        return None, details

    module_name, attr_path = producer.split(":", 1)
    if not module_name or not attr_path:
        details["error_reason_id"] = "unsupported_producer_function_format"
        return None, details

    try:
        module = importlib.import_module(module_name)
    except Exception as exc:  # pragma: no cover - exact import errors vary by environment
        details["error_reason_id"] = "producer_function_import_failed"
        details["import_error"] = f"{type(exc).__name__}: {exc}"
        return None, details

    target: Any = module
    try:
        for attr in attr_path.split("."):
            target = getattr(target, attr)
    except AttributeError as exc:
        details["error_reason_id"] = "producer_function_import_failed"
        details["import_error"] = f"{type(exc).__name__}: {exc}"
        return None, details

    if not callable(target):
        details["error_reason_id"] = "producer_function_not_callable"
        return None, details

    source_path_raw = inspect.getsourcefile(target) or inspect.getfile(target)
    if not source_path_raw:
        details["error_reason_id"] = "producer_source_unresolved"
        return None, details

    source_path = Path(source_path_raw).resolve()
    repo_root = _repo_root().resolve()
    try:
        source_path.relative_to(repo_root)
    except ValueError:
        details["error_reason_id"] = "producer_source_outside_repo"
        details["resolved_source_file_path"] = str(source_path)
        return None, details

    details["resolved_source_file_path"] = source_path.relative_to(repo_root).as_posix()
    details["resolved_code_hash"] = _sha256_bytes(source_path.read_bytes())
    details["callable_name"] = getattr(target, "__name__", attr_path)
    return target, details


def _bundle_input_hashes(
    bundle_path: Path,
    declared_inputs: Any,
    declared_hashes: Any,
) -> tuple[list[Path], dict[str, str], list[dict[str, Any]]]:
    reasons: list[dict[str, Any]] = []
    input_paths: list[Path] = []
    computed_hashes: dict[str, str] = {}
    bundle_root = bundle_path.resolve()

    if not isinstance(declared_inputs, list) or not declared_inputs:
        reasons.append(
            _reason(
                "missing_input_artifact_paths",
                "blocked_missing_callable_provenance",
                "metric_provenance.jsonl",
                "input_artifact_paths",
                "No declared input artifact paths were available for callable recomputation.",
            )
        )
        return input_paths, computed_hashes, reasons

    for declared_input in declared_inputs:
        if not isinstance(declared_input, str) or not declared_input.strip():
            reasons.append(
                _reason(
                    "invalid_input_artifact_path",
                    "blocked_missing_callable_provenance",
                    "metric_provenance.jsonl",
                    "input_artifact_paths",
                    f"Invalid input artifact path: {declared_input!r}.",
                )
            )
            continue
        candidate = (bundle_root / declared_input).resolve()
        try:
            candidate.relative_to(bundle_root)
        except ValueError:
            reasons.append(
                _reason(
                    "input_artifact_path_outside_bundle",
                    "blocked_missing_callable_provenance",
                    "metric_provenance.jsonl",
                    declared_input,
                    "Declared input artifact path resolves outside the evidence bundle.",
                )
            )
            continue
        if not candidate.exists() or not candidate.is_file():
            reasons.append(
                _reason(
                    "input_artifact_missing",
                    "blocked_missing_callable_provenance",
                    "metric_provenance.jsonl",
                    declared_input,
                    "Declared input artifact does not exist.",
                )
            )
            continue
        computed = _sha256_bytes(candidate.read_bytes())
        input_paths.append(candidate)
        computed_hashes[declared_input] = computed

    if isinstance(declared_hashes, dict):
        for declared_input, computed in computed_hashes.items():
            declared = _normalize_sha256(declared_hashes.get(declared_input))
            if declared is None:
                reasons.append(
                    _reason(
                        "input_artifact_hash_missing",
                        "blocked_missing_callable_provenance",
                        "metric_provenance.jsonl",
                        declared_input,
                        "No usable declared sha256 hash was found for the input artifact.",
                    )
                )
            elif declared != computed:
                reasons.append(
                    _reason(
                        "input_artifact_hash_mismatch",
                        "blocked_callable_provenance_mismatch",
                        "metric_provenance.jsonl",
                        declared_input,
                        "Computed input artifact hash does not match declared hash.",
                    )
                )
    else:
        reasons.append(
            _reason(
                "input_artifact_hashes_not_mapping",
                "blocked_missing_callable_provenance",
                "metric_provenance.jsonl",
                "input_artifact_hashes",
                "Input artifact hashes must be a mapping from path to sha256.",
            )
        )

    return input_paths, computed_hashes, reasons


def _call_producer(
    producer_callable: Any,
    input_paths: list[Path],
    run_id: str,
    aggregation_rule: str,
    row: dict[str, Any],
) -> tuple[dict[str, Any] | None, str | None]:
    try:
        with tempfile.TemporaryDirectory(prefix="eav001b_") as tmp:
            output_dir = Path(tmp)
            kwargs = {
                "input_paths": input_paths,
                "output_dir": output_dir,
                "run_id": run_id,
                "aggregation_rule": aggregation_rule,
            }
            signature = inspect.signature(producer_callable)
            if "row" in signature.parameters:
                kwargs["row"] = dict(row)
            result = producer_callable(**kwargs)
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"
    if not isinstance(result, dict):
        return None, "callable returned non-dict result"
    return result, None


def _validate_callable_provenance(
    row: dict[str, Any],
    index: int,
    bundle_path: Path,
    seen_run_ids: set[str],
) -> tuple[list[dict[str, Any]], dict[str, Any] | None, dict[str, Any]]:
    reasons: list[dict[str, Any]] = []
    producer = row.get("producer_function")
    run_id = row.get("run_id")
    aggregation_rule = row.get("aggregation_rule")
    check: dict[str, Any] = {
        "row_type": "metric_provenance",
        "row_index": index,
        "bundle_path": str(bundle_path),
        "producer_function": producer,
        "resolved_source_file_path": None,
        "resolved_code_hash": None,
        "declared_code_path_hash": row.get("code_path_hash"),
        "declared_inputs": row.get("input_artifact_paths"),
        "computed_input_hashes": {},
        "run_id": run_id,
        "aggregation_rule": aggregation_rule,
        "declared_output_digest": row.get("expected_output_digest"),
        "recomputed_output_digest": None,
        "recomputed_metric_value": None,
        "producer_callable_invoked": False,
        "admit_or_block_decision": "block",
        "block_reason_ids": [],
    }

    if not isinstance(run_id, str) or not run_id:
        reasons.append(
            _reason(
                "missing_metric_run_id",
                "blocked_missing_callable_provenance",
                "metric_provenance.jsonl",
                f"metric_provenance.jsonl[{index}]",
                "Metric row did not declare a non-empty run_id.",
            )
        )
    elif run_id in seen_run_ids:
        reasons.append(
            _reason(
                "duplicate_metric_run_id",
                "blocked_missing_callable_provenance",
                "metric_provenance.jsonl",
                f"metric_provenance.jsonl[{index}]",
                "Metric row reused a run_id that must uniquely identify one recomputation row.",
            )
        )
    else:
        seen_run_ids.add(run_id)

    if aggregation_rule not in SUPPORTED_AGGREGATION_RULES:
        reasons.append(
            _reason(
                "unsupported_aggregation_rule",
                "blocked_missing_callable_provenance",
                "metric_provenance.jsonl",
                f"metric_provenance.jsonl[{index}]",
                f"Unsupported aggregation rule: {aggregation_rule!r}.",
            )
        )

    if row.get("recompute_contract") != CALLABLE_RECOMPUTE_CONTRACT:
        reasons.append(
            _reason(
                "missing_recompute_contract",
                "blocked_missing_callable_provenance",
                "metric_provenance.jsonl",
                f"metric_provenance.jsonl[{index}]",
                f"Metric row lacks recompute_contract={CALLABLE_RECOMPUTE_CONTRACT!r}.",
            )
        )

    producer_callable, import_details = _import_callable(producer)
    check["resolved_source_file_path"] = import_details.get("resolved_source_file_path")
    check["resolved_code_hash"] = import_details.get("resolved_code_hash")
    if producer_callable is None:
        reason_id = import_details.get("error_reason_id", "producer_function_import_failed")
        reasons.append(
            _reason(
                reason_id,
                "blocked_missing_callable_provenance",
                "metric_provenance.jsonl",
                f"metric_provenance.jsonl[{index}]",
                f"Could not resolve callable producer_function {producer!r}: {import_details.get('import_error') or reason_id}.",
            )
        )

    declared_code_hash = _normalize_sha256(row.get("code_path_hash"))
    if producer_callable is not None:
        if declared_code_hash is None:
            reasons.append(
                _reason(
                    "code_path_hash_missing_or_invalid",
                    "blocked_missing_callable_provenance",
                    "metric_provenance.jsonl",
                    f"metric_provenance.jsonl[{index}]",
                    "Metric row did not declare a usable code_path_hash.",
                )
            )
        elif import_details["resolved_code_hash"] != declared_code_hash:
            reasons.append(
                _reason(
                    "code_path_hash_mismatch",
                    "blocked_callable_provenance_mismatch",
                    "metric_provenance.jsonl",
                    f"metric_provenance.jsonl[{index}]",
                    "Resolved producer source hash does not match declared code_path_hash.",
                )
            )

    input_paths, computed_hashes, input_reasons = _bundle_input_hashes(
        bundle_path,
        row.get("input_artifact_paths"),
        row.get("input_artifact_hashes"),
    )
    check["computed_input_hashes"] = computed_hashes
    reasons.extend(input_reasons)

    declared_output_digest = _normalize_sha256(row.get("expected_output_digest"))
    if declared_output_digest is None:
        reasons.append(
            _reason(
                "missing_expected_output_digest",
                "blocked_missing_callable_provenance",
                "metric_provenance.jsonl",
                f"metric_provenance.jsonl[{index}]",
                "Metric row did not declare expected_output_digest for recomputation.",
            )
        )

    may_call = (
        producer_callable is not None
        and not any(
            reason["reason_id"]
            in {
                "missing_metric_run_id",
                "duplicate_metric_run_id",
                "unsupported_aggregation_rule",
                "missing_recompute_contract",
                "code_path_hash_missing_or_invalid",
                "code_path_hash_mismatch",
                "missing_input_artifact_paths",
                "invalid_input_artifact_path",
                "input_artifact_path_outside_bundle",
                "input_artifact_missing",
                "input_artifact_hash_missing",
                "input_artifact_hash_mismatch",
                "input_artifact_hashes_not_mapping",
                "missing_expected_output_digest",
            }
            for reason in reasons
        )
    )
    if may_call:
        result, error = _call_producer(
            producer_callable,
            input_paths,
            run_id,
            aggregation_rule,
            row,
        )
        check["producer_callable_invoked"] = True
        if error is not None or result is None:
            reasons.append(
                _reason(
                    "producer_callable_execution_failed",
                    "blocked_missing_callable_provenance",
                    "metric_provenance.jsonl",
                    f"metric_provenance.jsonl[{index}]",
                    f"Callable producer failed during recomputation: {error}",
                )
            )
        else:
            recomputed_digest = _normalize_sha256(result.get("output_digest"))
            if recomputed_digest is None:
                reasons.append(
                    _reason(
                        "producer_result_missing_output_digest",
                        "blocked_missing_callable_provenance",
                        "metric_provenance.jsonl",
                        f"metric_provenance.jsonl[{index}]",
                        "Callable result did not contain a usable output_digest.",
                    )
                )
            else:
                check["recomputed_output_digest"] = recomputed_digest
                if declared_output_digest != recomputed_digest:
                    reasons.append(
                        _reason(
                            "output_digest_mismatch",
                            "blocked_callable_provenance_mismatch",
                            "metric_provenance.jsonl",
                            f"metric_provenance.jsonl[{index}]",
                            "Callable recomputation output digest did not match declared digest.",
                        )
                    )
            if "expected_metric_value" in row:
                check["recomputed_metric_value"] = result.get("metric_value")
                if result.get("metric_value") != row.get("expected_metric_value"):
                    reasons.append(
                        _reason(
                            "metric_value_mismatch",
                            "blocked_callable_provenance_mismatch",
                            "metric_provenance.jsonl",
                            f"metric_provenance.jsonl[{index}]",
                            "Callable recomputation metric value did not match declared metric value.",
                        )
                    )
            if "expected_output_row_count" in row and result.get("output_row_count") != row.get(
                "expected_output_row_count"
            ):
                reasons.append(
                    _reason(
                        "output_row_count_mismatch",
                        "blocked_callable_provenance_mismatch",
                        "metric_provenance.jsonl",
                        f"metric_provenance.jsonl[{index}]",
                        "Callable recomputation output row count did not match declared row count.",
                    )
                )

    row_reason_ids = [reason["reason_id"] for reason in reasons]
    check["block_reason_ids"] = row_reason_ids
    if not row_reason_ids:
        check["admit_or_block_decision"] = "admit"
        verified = {
            "row_type": "metric_provenance",
            "metric_id": row["metric_id"],
            "evidence_role": row["evidence_role"],
            "producer_function": producer,
            "run_id": run_id,
            "output_row_ids": row["output_row_ids"],
            "resolved_source_file_path": check["resolved_source_file_path"],
            "resolved_code_hash": check["resolved_code_hash"],
            "computed_input_hashes": computed_hashes,
            "recomputed_output_digest": check["recomputed_output_digest"],
            "computed": True,
        }
        return reasons, verified, check
    return reasons, None, check


def _called_functions(invocation_rows: list[dict[str, Any]]) -> set[str]:
    called = set()
    for row in invocation_rows:
        if row.get("called") is True:
            for key in ("producer_function", "function_name"):
                value = row.get(key)
                if isinstance(value, str) and value:
                    called.add(value)
    return called


def _validate_metric_rows(
    metric_rows: list[dict[str, Any]],
    invocation_rows: list[dict[str, Any]],
    bundle_path: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    reasons: list[dict[str, Any]] = []
    verified: list[dict[str, Any]] = []
    callable_checks: list[dict[str, Any]] = []
    called = _called_functions(invocation_rows)
    seen_run_ids: set[str] = set()

    if not metric_rows:
        reasons.append(
            _reason(
                "missing_metric_provenance",
                "blocked_missing_callable_provenance",
                "metric_provenance.jsonl",
                "metric_provenance.jsonl",
                "No metric provenance rows were found.",
            )
        )
        return reasons, verified, callable_checks

    for index, row in enumerate(metric_rows):
        missing = sorted(field for field in METRIC_REQUIRED_FIELDS if field not in row)
        producer = row.get("producer_function")
        output_ids = row.get("output_row_ids")
        if missing:
            reasons.append(
                _reason(
                    "metric_provenance_missing_required_fields",
                    "blocked_missing_callable_provenance",
                    "metric_provenance.jsonl",
                    f"metric_provenance.jsonl[{index}]",
                    "Missing required fields: " + ", ".join(missing),
                )
            )
            continue
        if not isinstance(producer, str) or not producer:
            reasons.append(
                _reason(
                    "metric_producer_missing_or_invalid",
                    "blocked_missing_callable_provenance",
                    "metric_provenance.jsonl",
                    f"metric_provenance.jsonl[{index}]",
                    "Metric row did not declare a usable producer_function.",
                )
            )
            continue
        if row.get("computed_not_literal") is not True or row.get("failure_path_available") is not True:
            reasons.append(
                _reason(
                    "metric_not_computed_or_no_failure_path",
                    "blocked_missing_callable_provenance",
                    "metric_provenance.jsonl",
                    f"metric_provenance.jsonl[{index}]",
                    "Metric row did not prove computed_not_literal and failure_path_available.",
                )
            )
            continue
        if not producer or producer not in called:
            reasons.append(
                _reason(
                    "metric_producer_not_invoked",
                    "blocked_missing_callable_provenance",
                    "invocation_ledger.jsonl",
                    f"metric_provenance.jsonl[{index}]",
                    f"Producer function was not invoked: {producer!r}.",
                )
            )
            continue
        if not isinstance(output_ids, list) or not output_ids:
            reasons.append(
                _reason(
                    "metric_missing_per_case_outputs",
                    "blocked_missing_callable_provenance",
                    "metric_provenance.jsonl",
                    f"metric_provenance.jsonl[{index}]",
                    "Metric row did not record per-case output row ids.",
                )
            )
            continue
        callable_reasons, verified_row, callable_check = _validate_callable_provenance(
            row,
            index,
            bundle_path,
            seen_run_ids,
        )
        reasons.extend(callable_reasons)
        callable_checks.append(callable_check)
        if callable_reasons:
            continue
        if verified_row is not None:
            verified.append(verified_row)

    return reasons, verified, callable_checks


def _has_role(metric_rows: list[dict[str, Any]], role: str) -> bool:
    return any(row.get("evidence_role") == role for row in metric_rows)


def _validate_baseline(bundle: dict[str, Any], metric_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = _rows_named(bundle, "baseline_invocations.jsonl")
    valid = [
        row
        for row in rows
        if row.get("called") is True
        and row.get("independent_callable") is True
        and row.get("computed_not_literal") is True
        and isinstance(row.get("output_row_ids"), list)
        and row.get("output_row_ids")
    ]
    if valid and _has_role(metric_rows, "baseline_metric"):
        return []
    return [
        _reason(
            "missing_callable_baseline_invocation",
            "blocked_missing_baseline",
            "baseline_invocations.jsonl",
            "baseline_invocations.jsonl",
            "No callable independent baseline invocation with per-case outputs was found.",
        )
    ]


def _validate_ablation(bundle: dict[str, Any], metric_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = _rows_named(bundle, "ablation_invocations.jsonl")
    valid = [
        row
        for row in rows
        if row.get("called") is True
        and row.get("intervention_applied") is True
        and row.get("episodes_rerun") is True
        and row.get("score_recomputed") is True
        and isinstance(row.get("output_row_ids"), list)
        and row.get("output_row_ids")
    ]
    if valid and _has_role(metric_rows, "ablation_metric"):
        return []
    return [
        _reason(
            "missing_ablation_rerun",
            "blocked_missing_ablation_rerun",
            "ablation_invocations.jsonl",
            "ablation_invocations.jsonl",
            "No ablation row proved intervention application, episode rerun, and score recomputation.",
        )
    ]


def _validate_leakage(bundle: dict[str, Any], metric_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    reports = _json_named(bundle, "leakage_scan_report.json")
    valid = [
        report
        for report in reports
        if report.get("called") is True
        and report.get("computed_not_literal") is True
        and isinstance(report.get("scanned_surfaces"), list)
        and report.get("scanned_surfaces")
        and report.get("positive_control_present") is True
        and report.get("positive_control_detected") is True
        and report.get("clean_control_passed") is True
    ]
    if valid and _has_role(metric_rows, "leakage_metric"):
        return []
    return [
        _reason(
            "missing_leakage_positive_control",
            "blocked_missing_leakage_positive_control",
            "leakage_scan_report.json",
            "leakage_scan_report.json",
            "Leakage scanner did not prove scanner invocation plus positive-control detection.",
        )
    ]


def _validate_replay(bundle: dict[str, Any], metric_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    reports = _json_named(bundle, "replay_recompute_report.json")
    valid = [
        report
        for report in reports
        if report.get("called") is True
        and report.get("computed_not_literal") is True
        and report.get("behavior_recomputed") is True
        and report.get("used_serialized_state") is True
        and report.get("used_observation") is True
        and report.get("compared_action") is True
        and report.get("hash_only") is not True
        and report.get("stored_actions_reused") is not True
    ]
    if valid and _has_role(metric_rows, "replay_metric"):
        return []
    return [
        _reason(
            "hash_only_replay",
            "blocked_missing_replay_recompute",
            "replay_recompute_report.json",
            "replay_recompute_report.json",
            "Replay did not prove behavior recomputation from serialized state plus observation.",
        )
    ]


def _validate_frozen_inputs(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    reports = _json_named(bundle, "frozen_input_consumption.json")
    if not reports:
        return [
            _reason(
                "missing_frozen_input_consumption",
                "blocked_missing_callable_provenance",
                "frozen_input_consumption.json",
                "frozen_input_consumption.json",
                "No frozen input consumption report was found.",
            )
        ]
    report = reports[0]
    required = set(report.get("required_input_ids", []))
    consumed = set(report.get("consumed_input_ids", []))
    unused = set(report.get("unused_input_ids", []))
    if required and required <= consumed and not unused:
        return []
    return [
        _reason(
            "unused_or_unconsumed_frozen_input",
            "blocked_missing_callable_provenance",
            "frozen_input_consumption.json",
            "frozen_input_consumption.json",
            "Frozen input ids were missing or not fully consumed.",
        )
    ]


def _claim_ceiling_present(bundle: dict[str, Any]) -> bool:
    return any(Path(path).name == "claim_ceiling.txt" for path in bundle["text_payloads"])


def _canonical_decision(reasons: list[dict[str, Any]]) -> str:
    if not reasons:
        return "admitted_for_citation"
    decisions = {reason["canonical_decision"] for reason in reasons}
    for decision in DECISION_PRECEDENCE:
        if decision in decisions:
            return decision
    return reasons[0]["canonical_decision"]


def verify_bundle(bundle_path: Path | str, run_id: str | None = None) -> dict[str, Any]:
    """Verify an evidence bundle by callable provenance and control rows only."""

    run_id = run_id or _now_run_id()
    bundle = _load_bundle(Path(bundle_path))
    invocation_rows = _rows_named(bundle, "invocation_ledger.jsonl")
    metric_rows = _rows_named(bundle, "metric_provenance.jsonl")
    reasons: list[dict[str, Any]] = []

    metric_reasons, verified_rows, callable_checks = _validate_metric_rows(
        metric_rows,
        invocation_rows,
        Path(bundle_path),
    )
    reasons.extend(metric_reasons)

    has_any_callable_provenance = bool(invocation_rows or metric_rows)
    if _has_pass_shaped_text(bundle) and not has_any_callable_provenance:
        reasons.insert(
            0,
            _reason(
                "fake_pass_without_callable_provenance",
                "blocked_fake_pass",
                "bundle_text_shape_scan",
                "result.json/report.md",
                "Pass-shaped result/report text exists without callable provenance rows.",
            ),
        )

    if not invocation_rows:
        reasons.append(
            _reason(
                "missing_invocation_ledger",
                "blocked_missing_callable_provenance",
                "invocation_ledger.jsonl",
                "invocation_ledger.jsonl",
                "No callable invocation ledger rows were found.",
            )
        )

    if not _claim_ceiling_present(bundle):
        reasons.append(
            _reason(
                "missing_claim_ceiling",
                "blocked_missing_callable_provenance",
                "claim_ceiling.txt",
                "claim_ceiling.txt",
                "No claim ceiling file was found.",
            )
        )

    if has_any_callable_provenance:
        reasons.extend(_validate_baseline(bundle, metric_rows))
        reasons.extend(_validate_ablation(bundle, metric_rows))
        reasons.extend(_validate_leakage(bundle, metric_rows))
        reasons.extend(_validate_replay(bundle, metric_rows))
        reasons.extend(_validate_frozen_inputs(bundle))

    if _has_claim_inflation(bundle):
        reasons.append(
            _reason(
                "claim_inflation_detected",
                "blocked_claim_inflation",
                "claim_ceiling_and_report_scan",
                "claim_ceiling.txt/report.md",
                "Forbidden readiness/mechanism/subjectivity claim language was detected.",
            )
        )

    canonical = _canonical_decision(reasons)
    block_matrix = {
        "task_id": TASK_ID,
        "blocking": canonical != "admitted_for_citation",
        "canonical_decision": canonical,
        "reasons": reasons,
        "verdict_text_used": False,
    }
    source_hash = _source_hash()
    decision = {
        "task_id": TASK_ID,
        "canonical_decision": canonical,
        "admitted_for_citation": canonical == "admitted_for_citation",
        "block_reason_ids": [reason["reason_id"] for reason in reasons],
        "block_reason_matrix": block_matrix,
        "verified_provenance_rows": verified_rows,
        "callable_provenance_checks": callable_checks,
        "fixture_manifest": {
            "bundle_path": str(bundle["bundle_path"]),
            "input_records": bundle["input_records"],
        },
        "producer_function": "verify_bundle",
        "producer_module": "evidence_admission_verifier_001a.core",
        "producer_source_path": PRODUCER_SOURCE_PATH,
        "code_path_hash": source_hash,
        "verifier_source_hashes": _verifier_source_hashes(),
        "run_id": run_id,
        "aggregation_rule": AGGREGATION_RULE,
        "decision_basis": "computed_bundle_evidence",
        "verdict_text_used": False,
        "claim_ceiling": CLAIM_CEILING,
        "what_this_does_not_prove": [
            "Gate validity",
            "mechanism validity",
            "Gate4 validity",
            "EGO readiness",
            "runtime readiness",
            "agency",
            "consciousness",
            "emotion",
            "autonomy",
            "stable user benefit",
        ],
    }
    return decision


def write_admission_artifacts(decision: dict[str, Any], output_dir: Path | str) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    verifier_command = decision.get("verifier_command", "library: verify_bundle")
    callable_checks = [
        {
            **check,
            "verifier_command": verifier_command,
            "output_artifact_path": str(out),
            "verifier_source_hashes": decision.get("verifier_source_hashes", {}),
        }
        for check in decision.get("callable_provenance_checks", [])
    ]

    result = {
        "task_id": TASK_ID,
        "admission_decision": decision["canonical_decision"],
        "admitted_for_citation": decision["admitted_for_citation"],
        "block_reason_ids": decision["block_reason_ids"],
        "producer_function": "write_admission_artifacts",
        "verifier_producer_function": decision["producer_function"],
        "run_id": decision["run_id"],
        "claim_ceiling": CLAIM_CEILING,
        "mainline_integration_status": "none",
        "enabled_status": "standalone CLI/library only",
        "real_trigger_evidence": "bundle JSON/JSONL rows parsed by verifier; callable provenance rows import, hash, input-hash, and recomputation checks must pass; verdict/report text not used as admissibility evidence",
        "callable_provenance_check_count": len(callable_checks),
        "verifier_source_hashes": decision.get("verifier_source_hashes", {}),
        "what_this_does_not_prove": decision["what_this_does_not_prove"],
    }

    _write_json(out / "result.json", result)
    _write_json(out / "admission_decision.json", {k: v for k, v in decision.items() if k != "verified_provenance_rows"})
    _write_json(out / "block_reason_matrix.json", decision["block_reason_matrix"])
    _write_jsonl(out / "verified_provenance_rows.jsonl", decision["verified_provenance_rows"])
    _write_jsonl(out / "callable_provenance_checks.jsonl", callable_checks)
    _write_json(out / "fixture_manifest.json", decision["fixture_manifest"])
    (out / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8")
