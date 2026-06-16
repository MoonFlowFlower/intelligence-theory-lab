from __future__ import annotations

import hashlib
import importlib
import inspect
import json
from pathlib import Path
from typing import Any, Callable


# A material provenance row is any dict carrying this marker. The walker
# (`collect_provenance_rows`) keys off the marker so that adding fields to a
# record never silently drops it from, or pulls an unrelated dict into, the
# provenance gate.
PROVENANCE_KIND = "material_record"

# Structural fields every material record must carry. The three governance
# attestations (computed_not_literal / threshold_frozen_before_run /
# failure_path_available) are NOT in this set on purpose: they are *computed by
# the validator*, never self-declared by the producer. A row that hardcodes them
# is checked against the computed value and rejected on disagreement.
REQUIRED_RECORD_FIELDS = {
    "provenance_kind",
    "value",
    "producer_function",
    "callable_source_path",
    "code_path_hash",
    "inputs",
    "run_id",
    "seed",
    "episode_ids",
    "aggregation",
    "threshold_used",
    "threshold_snapshot_hash",
    "subsystem",
    "recompute_basis",
}

# Attestation field names that must never be trusted if a producer writes them.
SELF_DECLARED_ATTESTATIONS = (
    "computed_not_literal",
    "threshold_frozen_before_run",
    "failure_path_available",
)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_text(json.dumps(value, sort_keys=True, separators=(",", ":")))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def source_path_for(function: Callable[..., Any]) -> str:
    source = inspect.getsourcefile(function)
    return Path(source or "<unknown>").as_posix()


def code_path_hash(function: Callable[..., Any]) -> str:
    return sha256_text(inspect.getsource(function))


def producer_name(function: Callable[..., Any]) -> str:
    return f"{function.__module__}.{function.__name__}"


def resolve_producer(name: str) -> Callable[..., Any] | None:
    """Resolve a 'module.function' string to the live callable, or None.

    Used by the validator to recompute a record's source hash from the *actual*
    importable producer. A fabricated row that names a producer which does not
    exist, or whose source no longer hashes to the recorded code_path_hash,
    therefore fails `computed_not_literal`.
    """
    if not isinstance(name, str) or "." not in name:
        return None
    module_name, _, attr = name.rpartition(".")
    try:
        module = importlib.import_module(module_name)
    except Exception:
        return None
    target = getattr(module, attr, None)
    return target if callable(target) else None


def config_source_hash(config_type: type) -> str:
    """Source hash of the frozen Config dataclass. Any threshold edit changes it."""
    return sha256_text(inspect.getsource(config_type))


def build_threshold_snapshot(*, config: Any, config_type: type) -> dict[str, Any]:
    """Capture the frozen thresholds + Config source hash BEFORE any gate runs.

    The snapshot hash is what every material record references; the validator
    recomputes it and the live Config source hash, so a post-hoc threshold edit
    is detectable (it changes config_source_hash) and a gate that compares
    against an undeclared threshold fails the freeze check.
    """
    declared = {
        "premise_band": round(float(config.premise_band), 6),
        "headroom_band": round(float(config.headroom_band), 6),
        "premise_threshold": round(float(config.premise_threshold), 6),
        "chance": round(float(config.chance), 6),
    }
    snapshot = {
        "declared_thresholds": declared,
        "config_source_hash": config_source_hash(config_type),
    }
    snapshot["snapshot_hash"] = sha256_json(snapshot)
    return snapshot


def _round6(value: float) -> float:
    return round(float(value), 6)


def recompute_value(recompute_basis: dict[str, Any]) -> float | None:
    """Re-derive a record's value from its declared basis (no hidden constants).

    Returns None if the basis is unrecognised/insufficient -> validator treats
    that as not-computed (block). This is what makes a hardcoded value fail:
    the basis must actually produce the reported number.
    """
    if not isinstance(recompute_basis, dict):
        return None
    kind = recompute_basis.get("kind")
    if kind == "mean":
        scores = recompute_basis.get("scores")
        if not isinstance(scores, list) or not scores:
            return None
        return _round6(sum(float(s) for s in scores) / len(scores))
    if kind == "max":
        values = recompute_basis.get("values")
        if not isinstance(values, list) or not values:
            return None
        return _round6(max(float(v) for v in values))
    if kind == "delta":
        if "minuend" not in recompute_basis or "subtrahend" not in recompute_basis:
            return None
        return _round6(float(recompute_basis["minuend"]) - float(recompute_basis["subtrahend"]))
    if kind == "indicator":
        if "predicate" not in recompute_basis:
            return None
        return 1.0 if bool(recompute_basis["predicate"]) else 0.0
    return None


def material_record(
    *,
    value: float,
    producer_function: Callable[..., Any],
    inputs: dict[str, Any],
    run_id: str,
    seed: int | str | None,
    episode_ids: list[str],
    aggregation: str,
    threshold_used: float | None,
    threshold_snapshot_hash: str,
    subsystem: str,
    recompute_basis: dict[str, Any],
) -> dict[str, Any]:
    """A provenance row for any score OR gate/verdict that feeds verdict selection.

    Carries a real source hash and a `recompute_basis`; the three governance
    attestations are deliberately absent (validator-computed).
    """
    return {
        "provenance_kind": PROVENANCE_KIND,
        "value": _round6(value),
        "producer_function": producer_name(producer_function),
        "callable_source_path": source_path_for(producer_function),
        "code_path_hash": code_path_hash(producer_function),
        "inputs": inputs,
        "run_id": run_id,
        "seed": seed,
        "episode_ids": episode_ids,
        "aggregation": aggregation,
        "threshold_used": (None if threshold_used is None else _round6(threshold_used)),
        "threshold_snapshot_hash": threshold_snapshot_hash,
        "subsystem": subsystem,
        "recompute_basis": recompute_basis,
    }


def aggregate_score_record(
    *,
    scores: list[float],
    producer_function: Callable[..., Any],
    inputs: dict[str, Any],
    run_id: str,
    episode_ids: list[str],
    threshold_used: float,
    threshold_snapshot_hash: str,
    subsystem: str,
    aggregation: str = "mean_episode_score",
) -> dict[str, Any]:
    mean_score = sum(scores) / len(scores) if scores else 0.0
    return material_record(
        value=mean_score,
        producer_function=producer_function,
        inputs=inputs,
        run_id=run_id,
        seed="multi_seed",
        episode_ids=episode_ids,
        aggregation=aggregation,
        threshold_used=threshold_used,
        threshold_snapshot_hash=threshold_snapshot_hash,
        subsystem=subsystem,
        recompute_basis={"kind": "mean", "scores": [_round6(s) for s in scores]},
    )


def collect_provenance_rows(payloads: list[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            if value.get("provenance_kind") == PROVENANCE_KIND:
                rows.append(value)
            for nested in value.values():
                walk(nested)
        elif isinstance(value, list):
            for nested in value:
                walk(nested)

    for payload in payloads:
        walk(payload)
    return rows


def _attestations_for_row(
    row: dict[str, Any],
    *,
    threshold_snapshot: dict[str, Any],
    failure_controls: dict[str, bool],
    live_config_source_hash: str,
) -> dict[str, bool]:
    # computed_not_literal: producer resolves AND its live source hashes to the
    # recorded code_path_hash AND the value is reproducible from the basis.
    producer = resolve_producer(row.get("producer_function", ""))
    producer_ok = producer is not None and code_path_hash(producer) == row.get("code_path_hash")
    recomputed = recompute_value(row.get("recompute_basis", {}))
    value_ok = recomputed is not None and recomputed == _round6(row.get("value", float("nan")))
    computed_not_literal = bool(producer_ok and value_ok)

    # threshold_frozen_before_run: snapshot referenced by the row matches the
    # pre-run snapshot, the Config source is unchanged since the snapshot, and
    # any numeric threshold used is one of the frozen declared thresholds.
    snapshot_ok = row.get("threshold_snapshot_hash") == threshold_snapshot.get("snapshot_hash")
    config_unchanged = threshold_snapshot.get("config_source_hash") == live_config_source_hash
    threshold_used = row.get("threshold_used")
    if threshold_used is None:
        threshold_declared = True
    else:
        declared_values = {
            _round6(v) for v in threshold_snapshot.get("declared_thresholds", {}).values()
        }
        threshold_declared = _round6(threshold_used) in declared_values
    threshold_frozen = bool(snapshot_ok and config_unchanged and threshold_declared)

    # failure_path_available: the subsystem this record belongs to actually had
    # its failure control flip a gate THIS run.
    failure_path_available = bool(failure_controls.get(row.get("subsystem"), False))

    return {
        "computed_not_literal": computed_not_literal,
        "threshold_frozen_before_run": threshold_frozen,
        "failure_path_available": failure_path_available,
    }


def validate_provenance_rows(
    rows: list[dict[str, Any]],
    *,
    threshold_snapshot: dict[str, Any],
    failure_controls: dict[str, bool],
    live_config_source_hash: str | None = None,
) -> dict[str, Any]:
    """Validate material rows with COMPUTED, fail-able attestations.

    Blocks (blocked_by_provenance_gap) on: missing structural fields, a producer
    that does not resolve / source-hash mismatch, a value not reproducible from
    its basis, a threshold not in the frozen snapshot, a subsystem whose failure
    control did not fire, OR a self-declared attestation that disagrees with the
    computed one (the hardcoded-True defence).
    """
    if live_config_source_hash is None:
        live_config_source_hash = threshold_snapshot.get("config_source_hash")
    failures: list[dict[str, Any]] = []
    per_row: list[dict[str, Any]] = []
    for index, row in enumerate(rows):
        missing = sorted(REQUIRED_RECORD_FIELDS - set(row))
        if missing:
            failures.append({"index": index, "reason": "missing_required_fields", "missing": missing})
            per_row.append({"index": index, "valid": False})
            continue
        attest = _attestations_for_row(
            row,
            threshold_snapshot=threshold_snapshot,
            failure_controls=failure_controls,
            live_config_source_hash=live_config_source_hash,
        )
        row_failures: list[str] = []
        if not attest["computed_not_literal"]:
            row_failures.append("not_computed_or_source_hash_mismatch")
        if not attest["threshold_frozen_before_run"]:
            row_failures.append("threshold_not_frozen")
        if not attest["failure_path_available"]:
            row_failures.append("failure_path_unavailable")
        # Hardcoded-attestation defence: if the row self-declares any attestation,
        # it must equal the computed one.
        for field in SELF_DECLARED_ATTESTATIONS:
            if field in row and bool(row[field]) != attest[field]:
                row_failures.append(f"self_declared_{field}_disagrees_with_computed")
        for reason in row_failures:
            failures.append(
                {
                    "index": index,
                    "reason": reason,
                    "producer_function": row.get("producer_function"),
                    "subsystem": row.get("subsystem"),
                }
            )
        per_row.append(
            {
                "index": index,
                "producer_function": row.get("producer_function"),
                "subsystem": row.get("subsystem"),
                "computed_attestations": attest,
                "valid": not row_failures,
            }
        )
    return {
        "provenance_kind": "validation_summary",
        "producer_function": producer_name(validate_provenance_rows),
        "code_path_hash": code_path_hash(validate_provenance_rows),
        "row_count": len(rows),
        "subsystems_covered": sorted({row.get("subsystem") for row in rows if "subsystem" in row}),
        "failure_controls": dict(sorted(failure_controls.items())),
        "valid": not failures,
        "failures": failures,
        "per_row": per_row,
        "verdict": "provenance_valid" if not failures else "blocked_by_provenance_gap",
    }
