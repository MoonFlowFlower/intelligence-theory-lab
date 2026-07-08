"""Frozen baseline battery and verdict logic for the Phase-A headroom probe."""
from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
import json
import random
from pathlib import Path
from typing import Any

from .adapters import ProbeRecord, canonical_json
from .contract import EQUIVALENCE_BAND, FAIR_BASELINE_FLOOR, CONTROL_EXPECTED_VERDICTS


def seed_everything(seed: int) -> dict[str, Any]:
    """Seed Python, NumPy, and torch-if-present explicitly."""

    seed_i = int(seed)
    random.seed(seed_i)
    report: dict[str, Any] = {"python_random_seed": seed_i}
    try:
        import numpy as np  # type: ignore

        np.random.seed(seed_i)
        report["numpy_seed"] = seed_i
    except Exception as exc:  # pragma: no cover - depends on local env
        report["numpy_seed"] = f"unavailable:{type(exc).__name__}"
    try:
        import torch  # type: ignore

        torch.manual_seed(seed_i)
        if hasattr(torch, "cuda"):
            torch.cuda.manual_seed_all(seed_i)
        report["torch_seed"] = seed_i
    except Exception as exc:
        report["torch_seed"] = f"not_used_or_unavailable:{type(exc).__name__}"
    return report


def code_path_hash() -> str:
    base = Path(__file__).resolve().parent
    h = sha256()
    for name in ("__init__.py", "adapters.py", "battery.py", "contract.py", "runner.py"):
        path = base / name
        if path.exists():
            h.update(name.encode("utf-8"))
            h.update(b"\0")
            h.update(path.read_bytes())
            h.update(b"\0")
    return h.hexdigest()


def _label_space(records: list[ProbeRecord]) -> tuple[str, ...]:
    labels = sorted({label for record in records for label in record.y})
    return tuple(labels)


def _train_eval(records: list[ProbeRecord]) -> tuple[list[ProbeRecord], list[ProbeRecord]]:
    train = [record for record in records if record.split == "train"]
    eval_rows = [record for record in records if record.split == "eval"]
    if not eval_rows:
        raise ValueError("adapter emitted no eval records")
    return train, eval_rows


def set_f1_score(truth: tuple[str, ...], pred: tuple[str, ...]) -> float:
    t = set(truth)
    p = set(pred)
    if not t and not p:
        return 1.0
    if not t or not p:
        return 0.0
    tp = len(t & p)
    denom = 2 * tp + len(p - t) + len(t - p)
    return 0.0 if denom == 0 else (2 * tp) / denom


def aggregate_score(eval_rows: list[ProbeRecord], predictions: list[tuple[str, ...]]) -> float:
    if len(eval_rows) != len(predictions):
        raise ValueError("prediction count does not match eval record count")
    return float(
        sum(set_f1_score(row.y, pred) for row, pred in zip(eval_rows, predictions))
        / len(eval_rows)
    )


def _majority_label(train: list[ProbeRecord], default: str = "") -> tuple[str, ...]:
    counts: Counter[str] = Counter(label for row in train for label in row.y)
    if not counts:
        return (default,) if default else tuple()
    return (counts.most_common(1)[0][0],)


def _fingerprint_observation(O: dict[str, Any]) -> str:
    return canonical_json(O)


def _predict_all(label_space: tuple[str, ...], eval_rows: list[ProbeRecord]) -> list[tuple[str, ...]]:
    return [label_space for _ in eval_rows]


def _predict_none(eval_rows: list[ProbeRecord]) -> list[tuple[str, ...]]:
    return [tuple() for _ in eval_rows]


def _per_user_lookup(train: list[ProbeRecord], eval_rows: list[ProbeRecord]) -> list[tuple[str, ...]]:
    table: dict[tuple[str, str], tuple[str, ...]] = {}
    group_majority: dict[str, tuple[str, ...]] = {}
    grouped: dict[str, list[ProbeRecord]] = defaultdict(list)
    for row in train:
        grouped[row.group_id].append(row)
        key = row.O.get("lookup_key")
        if key is not None:
            table[(row.group_id, str(key))] = row.y
    for group_id, rows in grouped.items():
        group_majority[group_id] = _majority_label(rows)
    global_majority = _majority_label(train)
    preds: list[tuple[str, ...]] = []
    for row in eval_rows:
        key = row.O.get("lookup_key")
        preds.append(
            table.get((row.group_id, str(key)), group_majority.get(row.group_id, global_majority))
        )
    return preds


def _count_table(train: list[ProbeRecord], eval_rows: list[ProbeRecord]) -> list[tuple[str, ...]]:
    table: dict[str, Counter[str]] = defaultdict(Counter)
    for row in train:
        key = str(row.O.get("cache_key", _fingerprint_observation(row.O)))
        for label in row.y:
            table[key][label] += 1
    global_majority = _majority_label(train)
    preds: list[tuple[str, ...]] = []
    for row in eval_rows:
        key = str(row.O.get("cache_key", _fingerprint_observation(row.O)))
        if key in table:
            preds.append((table[key].most_common(1)[0][0],))
        else:
            preds.append(global_majority)
    return preds


def _nearest_neighbor(train: list[ProbeRecord], eval_rows: list[ProbeRecord]) -> list[tuple[str, ...]]:
    if not train:
        return [tuple() for _ in eval_rows]
    train_keys = [set(canonical_json(row.O).split(",")) for row in train]
    preds: list[tuple[str, ...]] = []
    for row in eval_rows:
        key = set(canonical_json(row.O).split(","))
        best_idx = max(
            range(len(train)),
            key=lambda i: len(key & train_keys[i]) / max(1, len(key | train_keys[i])),
        )
        preds.append(train[best_idx].y)
    return preds


def _frequency_marginal(train: list[ProbeRecord], eval_rows: list[ProbeRecord]) -> list[tuple[str, ...]]:
    seen_by_group: dict[str, set[str]] = defaultdict(set)
    for row in train:
        value = row.O.get("frequency_value")
        if value is not None:
            seen_by_group[row.group_id].add(str(value))
    majority = _majority_label(train)
    # Binary contamination-like adapters may use this convention; otherwise
    # fallback to global majority to avoid inventing a label.
    contamination_label = ("contaminated",)
    preds: list[tuple[str, ...]] = []
    for row in eval_rows:
        value = row.O.get("frequency_value")
        if value is not None and seen_by_group[row.group_id] and str(value) not in seen_by_group[row.group_id]:
            preds.append(contamination_label)
        else:
            preds.append(majority)
    return preds


def _graph_closure(eval_rows: list[ProbeRecord]) -> list[tuple[str, ...]]:
    preds: list[tuple[str, ...]] = []
    for row in eval_rows:
        O = row.O
        relation_pairs = O.get("relation_pairs")
        asserted = O.get("asserted_tuple")
        if relation_pairs is None or asserted is None:
            preds.append(tuple())
            continue
        try:
            first = int(asserted[0][1])
            second = int(asserted[1][1])
            legal = {(int(a), int(b)) for a, b in relation_pairs}
            preds.append(("genuine",) if (first, second) in legal else ("contaminated",))
        except Exception:
            preds.append(tuple())
    return preds


def _obs_only_decoder(train: list[ProbeRecord], eval_rows: list[ProbeRecord]) -> list[tuple[str, ...]]:
    table: dict[str, Counter[str]] = defaultdict(Counter)
    for row in train:
        table[_fingerprint_observation(row.O)].update(row.y)
    majority = _majority_label(train)
    preds: list[tuple[str, ...]] = []
    for row in eval_rows:
        key = _fingerprint_observation(row.O)
        if key in table:
            preds.append((table[key].most_common(1)[0][0],))
        else:
            preds.append(majority)
    return preds


def _ideal_oracle(eval_rows: list[ProbeRecord]) -> list[tuple[str, ...]]:
    return [row.y_star for row in eval_rows]


def shuffle_o_y(records: list[ProbeRecord], seed: int) -> list[ProbeRecord]:
    """Seeded target permutation over eval records, preserving oracle ceiling."""

    rng = random.Random(int(seed))
    eval_targets = [row.y for row in records if row.split == "eval"]
    shuffled = list(eval_targets)
    rng.shuffle(shuffled)
    out: list[ProbeRecord] = []
    idx = 0
    for row in records:
        if row.split != "eval":
            out.append(row)
            continue
        y = shuffled[idx]
        idx += 1
        out.append(
            ProbeRecord(
                record_id=row.record_id,
                split=row.split,
                group_id=row.group_id,
                O=row.O,
                y=y,
                y_star=y,
            )
        )
    return out


def run_battery(
    records: list[ProbeRecord],
    *,
    seed: int,
    include_graph_closure: bool = True,
    shuffle_targets: bool = False,
) -> dict[str, Any]:
    """Run the callable baseline battery over supplied records.

    This function is the shared computation path.  Phase A tests use synthetic
    records only; official control/candidate use requires Phase-B authorization
    at the CLI boundary.
    """

    seed_report = seed_everything(seed)
    working = shuffle_o_y(records, seed) if shuffle_targets else list(records)
    train, eval_rows = _train_eval(working)
    label_space = _label_space(working)
    predictions: dict[str, list[tuple[str, ...]]] = {
        "predict_all": _predict_all(label_space, eval_rows),
        "predict_none": _predict_none(eval_rows),
        "per_user_lookup": _per_user_lookup(train, eval_rows),
        "nearest_neighbor": _nearest_neighbor(train, eval_rows),
        "count_table": _count_table(train, eval_rows),
        "frequency_marginal": _frequency_marginal(train, eval_rows),
        "obs_only_decoder": _obs_only_decoder(train, eval_rows),
        "ideal_oracle": _ideal_oracle(eval_rows),
    }
    if include_graph_closure:
        predictions["graph_closure"] = _graph_closure(eval_rows)
    scores = {
        name: aggregate_score(eval_rows, preds)
        for name, preds in sorted(predictions.items())
    }
    return {
        "producer_function": "run_battery",
        "seed_report": seed_report,
        "seed": int(seed),
        "record_count": len(working),
        "eval_record_count": len(eval_rows),
        "include_graph_closure": bool(include_graph_closure),
        "shuffle_targets": bool(shuffle_targets),
        "scores": scores,
        "verdict": evaluate_verdict(scores, equivalence_band=EQUIVALENCE_BAND),
        "code_path_hash": code_path_hash(),
    }


def evaluate_verdict(scores: dict[str, float], *, equivalence_band: float) -> dict[str, Any]:
    """Compute HEADROOM vs SATURATED from score data, not expected literals."""

    if "ideal_oracle" not in scores:
        raise ValueError("scores must include ideal_oracle")
    fair_scores = {
        name: float(scores[name])
        for name in FAIR_BASELINE_FLOOR
        if name in scores
    }
    if not fair_scores:
        raise ValueError("no fair baseline scores present")
    strongest_id, strongest_score = max(fair_scores.items(), key=lambda kv: kv[1])
    ceiling = float(scores["ideal_oracle"])
    gap = ceiling - strongest_score
    verdict = "HEADROOM" if gap > float(equivalence_band) else "SATURATED"
    return {
        "producer_function": "evaluate_verdict",
        "ceiling_score": ceiling,
        "strongest_fair_baseline_id": strongest_id,
        "strongest_fair_baseline_score": strongest_score,
        "equivalence_band": float(equivalence_band),
        "gap": gap,
        "verdict": verdict,
        "aggregation_rule": "HEADROOM iff ideal_oracle - max(fair floor) > equivalence_band; otherwise SATURATED",
    }


def probe_valid_gate(control_verdicts: dict[str, str]) -> dict[str, Any]:
    mismatches = {
        env_id: {
            "expected": expected,
            "observed": control_verdicts.get(env_id),
        }
        for env_id, expected in CONTROL_EXPECTED_VERDICTS.items()
        if control_verdicts.get(env_id) != expected
    }
    return {
        "producer_function": "probe_valid_gate",
        "expected": dict(CONTROL_EXPECTED_VERDICTS),
        "observed": dict(control_verdicts),
        "mismatches": mismatches,
        "probe_valid": not mismatches,
        "candidate_verdict_policy": "ALLOW_CANDIDATE_VERDICTS" if not mismatches else "VOID_ALL_CANDIDATE_VERDICTS",
    }


def stable_digest(payload: dict[str, Any]) -> str:
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
