import hashlib
import inspect
from pathlib import Path
from typing import Any, Callable

from .config import THRESHOLDS_FROZEN_BEFORE_RUN


REQUIRED_FIELDS = {
    "metric_id",
    "metric_name",
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


def code_path_hash(function: Callable[..., Any] | str) -> str:
    if isinstance(function, str):
        payload = function.encode("utf-8")
    else:
        try:
            payload = inspect.getsource(function).encode("utf-8")
        except OSError:
            payload = repr(function).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _hash_existing_inputs(paths: list[str]) -> dict[str, str]:
    hashes = {}
    for raw_path in paths:
        path = Path(raw_path)
        if path.exists() and path.is_file():
            hashes[raw_path] = "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            hashes[raw_path] = "not_available_until_artifact_write"
    return hashes


def build_metric_provenance(
    *,
    metric_id: str,
    metric_name: str,
    producer_function: str,
    producer_module: str,
    code_path_hash: str,
    run_id: str,
    seed_ids: list[int] | list[str],
    episode_ids: list[str],
    input_artifact_paths: list[str],
    output_artifact_path: str,
    output_row_ids: list[str],
    aggregation_rule: str,
    threshold_used: float,
    computed_not_literal_evidence: str | None = None,
    failure_path_evidence: str | None = None,
    train_context_ids_consumed: list[str] | None = None,
    heldout_context_ids_consumed: list[str] | None = None,
    counterfactual_pair_ids_consumed: list[str] | None = None,
    input_row_count: int | None = None,
) -> dict:
    computed_not_literal = bool(
        computed_not_literal_evidence
        and producer_function
        and producer_module
        and code_path_hash
        and aggregation_rule != "literal"
        and output_row_ids
    )
    failure_path_available = bool(failure_path_evidence)
    return {
        "metric_id": metric_id,
        "metric_name": metric_name,
        "producer_function": producer_function,
        "producer_module": producer_module,
        "code_path_hash": code_path_hash,
        "run_id": run_id,
        "episode_ids": episode_ids,
        "seed_ids": list(seed_ids),
        "train_context_ids_consumed": train_context_ids_consumed or ["not_applicable:no_training_context"],
        "heldout_context_ids_consumed": heldout_context_ids_consumed or episode_ids,
        "counterfactual_pair_ids_consumed": counterfactual_pair_ids_consumed
        or ["not_applicable:no_counterfactual_pair"],
        "input_artifact_paths": input_artifact_paths,
        "input_artifact_hashes": _hash_existing_inputs(input_artifact_paths),
        "input_row_count": input_row_count if input_row_count is not None else len(episode_ids),
        "output_artifact_path": output_artifact_path,
        "output_row_ids": output_row_ids,
        "aggregation_rule": aggregation_rule,
        "threshold_used": threshold_used,
        "threshold_frozen_before_run": THRESHOLDS_FROZEN_BEFORE_RUN,
        "computed_not_literal": computed_not_literal,
        "computed_not_literal_evidence": computed_not_literal_evidence
        or "missing:computed_evidence_not_supplied",
        "failure_path_available": failure_path_available,
        "failure_path_evidence": failure_path_evidence or "missing:failure_path_not_supplied",
    }


def validate_metric_provenance(row: dict) -> dict:
    errors = sorted(field for field in REQUIRED_FIELDS if field not in row)
    if (
        not row.get("producer_function")
        or not row.get("producer_module")
        or not row.get("code_path_hash")
        or row.get("computed_not_literal") is not True
    ):
        errors.append("missing_or_literal_producer")
    if row.get("failure_path_available") is not True:
        errors.append("missing_failure_path")
    if row.get("threshold_frozen_before_run") is not True:
        errors.append("threshold_not_frozen")
    return {"valid": not errors, "errors": sorted(set(errors))}
