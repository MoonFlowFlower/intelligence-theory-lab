"""S3b graph-cache family fitted from prefix-only member-view streams."""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
from pathlib import Path
import time
from typing import Any, Iterable, Mapping, Sequence

from .base import (
    PrefixEvent,
    Prediction,
    distribution_from_counts,
    event_from_mapping,
    prediction_for_all_actions,
    response_alphabet_size,
)


GRAPH_CACHE_MEMBER_NAMES = [
    "successor_map",
    "transition_table",
    "count_table",
    "fsm_planner",
    "episodic_traversal",
]

Key = tuple[Any, ...]


class _GraphCachePredictor:
    name = "graph_cache_base"
    key_construction = "override"

    def __init__(self, alphabet_size: int, turns_per_session: int):
        self.alphabet_size = int(alphabet_size)
        self.turns_per_session = int(turns_per_session)
        self._table: dict[Key, list[float]] = defaultdict(lambda: [0.0] * self.alphabet_size)
        self._action_counts: dict[str, list[float]] = defaultdict(lambda: [0.0] * self.alphabet_size)
        self._global_counts = [0.0] * self.alphabet_size
        self._prefix: list[PrefixEvent] = []

    @classmethod
    def from_design(cls, design: Mapping[str, Any]):
        _require_member(design, cls.name)
        return cls(
            response_alphabet_size(design),
            int(design["env_parameters"]["episodes"]["T_turns_per_session"]),
        )

    @property
    def distinct_key_count(self) -> int:
        return len(self._table)

    @property
    def total_observations(self) -> int:
        return int(sum(sum(counts) for counts in self._table.values()))

    def fit(self, records: Iterable[PrefixEvent | Mapping[str, Any]]) -> None:
        self.reset()
        for record in records:
            self.observe(record)

    def reset(self) -> None:
        self._table.clear()
        self._action_counts.clear()
        self._global_counts = [0.0] * self.alphabet_size
        self._prefix = []

    def observe(self, event: PrefixEvent | Mapping[str, Any]) -> None:
        parsed = event_from_mapping(event)
        if parsed.step_index == 0:
            self._prefix = []
        key = self.key_for_event(parsed, self._prefix)
        symbol = int(parsed.observation["symbol"])
        self._table[key][symbol] += 1.0
        self._action_counts[parsed.action][symbol] += 1.0
        self._global_counts[symbol] += 1.0
        self._prefix.append(parsed)

    def predict(self, counterfactual_actions: Sequence[str]) -> Prediction:
        if not self._prefix:
            return prediction_for_all_actions(counterfactual_actions, distribution_from_counts(self._global_counts))
        out: Prediction = {}
        context = self._next_context()
        for action in counterfactual_actions:
            key = self.key_for_prediction(str(action), context, self._prefix)
            counts = self._table.get(key)
            if counts is None or sum(counts) <= 0.0:
                counts = self._action_counts.get(str(action), self._global_counts)
            out[str(action)] = distribution_from_counts(counts)
        return out

    def key_for_event(self, event: PrefixEvent, prefix: Sequence[PrefixEvent]) -> Key:
        context = {
            "session_index": int(event.session_index),
            "turn_in_session": int(event.turn_in_session),
            "session_boundary": str(event.session_boundary),
        }
        return self.key_for_prediction(str(event.action), context, prefix)

    def key_for_prediction(self, action: str, context: Mapping[str, Any], prefix: Sequence[PrefixEvent]) -> Key:
        raise NotImplementedError

    def collision_statistics(self) -> dict[str, Any]:
        symbol_counts_per_key = [sum(1 for value in counts if value > 0.0) for counts in self._table.values()]
        totals = [sum(counts) for counts in self._table.values()]
        return {
            "total_observations": self.total_observations,
            "keys_with_multiple_symbols": sum(1 for count in symbol_counts_per_key if count > 1),
            "max_symbols_per_key": max(symbol_counts_per_key, default=0),
            "max_records_per_key": int(max(totals, default=0)),
        }

    def _next_context(self) -> dict[str, Any]:
        last = self._prefix[-1]
        next_step = int(last.step_index) + 1
        next_turn = next_step % self.turns_per_session
        return {
            "session_index": next_step // self.turns_per_session,
            "turn_in_session": next_turn,
            "session_boundary": "start" if next_turn == 0 else "none",
        }


class SuccessorMapPredictor(_GraphCachePredictor):
    name = "successor_map"
    key_construction = "previous observed symbol plus candidate action"

    def key_for_prediction(self, action: str, context: Mapping[str, Any], prefix: Sequence[PrefixEvent]) -> Key:
        previous = int(prefix[-1].observation["symbol"]) if prefix else None
        return ("prev_symbol", previous, "action", str(action))


class TransitionTablePredictor(_GraphCachePredictor):
    name = "transition_table"
    key_construction = "session boundary, turn-in-session, and candidate action"

    def key_for_prediction(self, action: str, context: Mapping[str, Any], prefix: Sequence[PrefixEvent]) -> Key:
        return (
            "boundary",
            str(context["session_boundary"]),
            "turn",
            int(context["turn_in_session"]),
            "action",
            str(action),
        )


class CountTablePredictor(_GraphCachePredictor):
    name = "count_table"
    key_construction = "candidate action only"

    def key_for_prediction(self, action: str, context: Mapping[str, Any], prefix: Sequence[PrefixEvent]) -> Key:
        return ("action", str(action))


class FsmPlannerPredictor(_GraphCachePredictor):
    name = "fsm_planner"
    key_construction = "coarse session index, turn-in-session, previous symbol, and candidate action"

    def key_for_prediction(self, action: str, context: Mapping[str, Any], prefix: Sequence[PrefixEvent]) -> Key:
        previous = int(prefix[-1].observation["symbol"]) if prefix else None
        session_bucket = min(int(context["session_index"]), 3)
        return (
            "session_bucket",
            session_bucket,
            "turn",
            int(context["turn_in_session"]),
            "prev_symbol",
            previous,
            "action",
            str(action),
        )


class EpisodicTraversalPredictor(_GraphCachePredictor):
    name = "episodic_traversal"
    key_construction = "last two action-symbol pairs and candidate action"

    def key_for_prediction(self, action: str, context: Mapping[str, Any], prefix: Sequence[PrefixEvent]) -> Key:
        tail = tuple((event.action, int(event.observation["symbol"])) for event in prefix[-2:])
        return ("tail2", tail, "action", str(action))


GRAPH_CACHE_CLASSES = {
    cls.name: cls
    for cls in (
        SuccessorMapPredictor,
        TransitionTablePredictor,
        CountTablePredictor,
        FsmPlannerPredictor,
        EpisodicTraversalPredictor,
    )
}


def graph_cache_conventions() -> dict[str, dict[str, str]]:
    return {
        name: {
            "key_construction": cls.key_construction,
            "fallback": "action-local empirical distribution, then global empirical distribution, then uniform",
        }
        for name, cls in GRAPH_CACHE_CLASSES.items()
    }


def fitting_data_contract(design: Mapping[str, Any]) -> dict[str, Any]:
    regimes = design["evaluation_regimes_per_gap"]
    if regimes["gap1"] != "LOG-PARITY" or regimes["gap3"] != "LOG-PARITY":
        raise ValueError("S3b predictor-class fitting requires frozen LOG-PARITY gap1/gap3 regimes")
    population = design["population_and_data"]
    seeds = list(population["env_master_seeds"])
    if not population.get("train_heldout_disjoint"):
        raise ValueError("S3b fitting requires frozen train_heldout_disjoint=true")
    return {
        "regime": "LOG-PARITY",
        "fit_partition": "train",
        "coverage_partition_reported": "heldout",
        "sets": [f"set_{index:02d}" for index, _ in enumerate(seeds)],
        "env_master_seeds": [int(seed) for seed in seeds],
        "member_view_fields_only": True,
        "source_fields": [
            "evaluation_regimes_per_gap.gap1",
            "evaluation_regimes_per_gap.gap3",
            "population_and_data.N_train_users",
            "population_and_data.N_heldout_users",
            "population_and_data.env_master_seeds",
            "population_and_data.train_heldout_disjoint",
        ],
    }


def build_graph_cache_alias_report(
    member: str,
    predictor: _GraphCachePredictor,
    train_records: Iterable[PrefixEvent | Mapping[str, Any]],
    heldout_records: Iterable[PrefixEvent | Mapping[str, Any]],
    *,
    design: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    train_summary = summarize_key_coverage(predictor, train_records, fitted_keys=set(predictor._table))
    heldout_summary = summarize_key_coverage(predictor, heldout_records, fitted_keys=set(predictor._table))
    return {
        "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
        "stage": "S3b",
        "artifact": f"s3b_alias_report_{member}",
        "member": member,
        "key_construction": graph_cache_conventions()[member]["key_construction"],
        "fitting_data_contract": fitting_data_contract(design) if design is not None else _default_contract(),
        "distinct_key_count": predictor.distinct_key_count,
        "collision_aliasing_statistics": predictor.collision_statistics(),
        "train_key_coverage": train_summary,
        "heldout_key_coverage": heldout_summary,
        "heldout_records_used_for_fitting": False,
        "producer_function": "src.fsp_pum_env.battery.graph_cache.build_graph_cache_alias_report",
        "run_started_at": _utc_timestamp(),
        "run_finished_at": _utc_timestamp(),
        "claim_ceiling": "S3b alias/key coverage instrumentation only; no gap or baseline-power claim",
    }


def summarize_key_coverage(
    predictor: _GraphCachePredictor,
    records: Iterable[PrefixEvent | Mapping[str, Any]],
    *,
    fitted_keys: set[Key],
) -> dict[str, Any]:
    prefix: list[PrefixEvent] = []
    observed: Counter[Key] = Counter()
    total_records = 0
    for record in records:
        parsed = event_from_mapping(record)
        if parsed.step_index == 0:
            prefix = []
        key = predictor.key_for_event(parsed, prefix)
        observed[key] += 1
        prefix.append(parsed)
        total_records += 1
    covered = sum(1 for key in observed if key in fitted_keys)
    return {
        "total_records": total_records,
        "total_keys": len(observed),
        "keys_seen_in_fitted_table": covered,
        "coverage_fraction": (covered / len(observed)) if observed else 0.0,
    }


def graph_cache_code_hash() -> str:
    h = hashlib.sha256()
    for path in (Path(__file__), Path(__file__).with_name("base.py")):
        h.update(path.name.encode("utf-8"))
        h.update(path.read_bytes())
    return h.hexdigest()


def _require_member(design: Mapping[str, Any], member: str) -> None:
    if member not in design["battery_membership"]["members"]:
        raise ValueError(f"frozen battery_membership missing {member}")


def _default_contract() -> dict[str, Any]:
    return {
        "regime": "LOG-PARITY",
        "fit_partition": "train",
        "coverage_partition_reported": "heldout",
        "member_view_fields_only": True,
    }


def _utc_timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
