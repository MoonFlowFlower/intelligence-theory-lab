"""S3c sequence-model battery members."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from .base import (
    PrefixEvent,
    Prediction,
    distribution_from_counts,
    event_from_mapping,
    prediction_for_all_actions,
    response_alphabet_size,
)
from . import obs_decoders


SEQUENCE_MEMBER_NAMES = [
    "seq_full_history_no_action_conditioning",
    "seq_window_with_action_conditioning_W15_no_cross_session_persistence",
]
W15 = 15


class SeqFullHistoryNoActionConditioningPredictor:
    name = "seq_full_history_no_action_conditioning"

    def __init__(self, alphabet_size: int):
        self.alphabet_size = int(alphabet_size)
        self.prefix_events: list[PrefixEvent] = []
        self._counts = [0.0] * self.alphabet_size

    @classmethod
    def from_design(cls, design: Mapping[str, Any]) -> "SeqFullHistoryNoActionConditioningPredictor":
        _require_member(design, cls.name)
        return cls(response_alphabet_size(design))

    def observe(self, event: PrefixEvent | Mapping[str, Any]) -> None:
        parsed = event_from_mapping(event)
        self.prefix_events.append(parsed)
        self._counts[int(parsed.observation["symbol"])] += 1.0

    def predict(self, counterfactual_actions: Sequence[str]) -> Prediction:
        distribution = distribution_from_counts(self._counts)
        return prediction_for_all_actions(counterfactual_actions, distribution)


class SeqWindowActionW15NoPersistencePredictor:
    name = "seq_window_with_action_conditioning_W15_no_cross_session_persistence"

    def __init__(self, alphabet_size: int):
        self.alphabet_size = int(alphabet_size)
        self.prefix_events: list[PrefixEvent] = []

    @classmethod
    def from_design(cls, design: Mapping[str, Any]) -> "SeqWindowActionW15NoPersistencePredictor":
        _require_member(design, cls.name)
        return cls(response_alphabet_size(design))

    def observe(self, event: PrefixEvent | Mapping[str, Any]) -> None:
        self.prefix_events.append(event_from_mapping(event))

    def predict(self, counterfactual_actions: Sequence[str]) -> Prediction:
        counts = [0.0] * self.alphabet_size
        for _, symbol in build_w15_action_conditioned_sequence(self.prefix_events):
            counts[int(symbol)] += 1.0
        distribution = distribution_from_counts(counts)
        return prediction_for_all_actions(counterfactual_actions, distribution)


def build_full_history_symbol_sequence(prefix_events: Sequence[PrefixEvent | Mapping[str, Any]]) -> list[int]:
    return [int(event_from_mapping(event).observation["symbol"]) for event in prefix_events]


def build_w15_action_conditioned_sequence(prefix_events: Sequence[PrefixEvent | Mapping[str, Any]]) -> list[tuple[str, int]]:
    parsed = [event_from_mapping(event) for event in prefix_events]
    last_boundary_index = 0
    for idx, event in enumerate(parsed):
        if event.session_boundary == "start":
            last_boundary_index = idx
    in_session = parsed[last_boundary_index:]
    return [(event.action, int(event.observation["symbol"])) for event in in_session[-W15:]]


def sequence_grid(member_name: str) -> list[dict[str, Any]]:
    if member_name not in SEQUENCE_MEMBER_NAMES:
        raise ValueError(f"unknown S3c sequence member: {member_name}")
    return obs_decoders._gru_grid(member_name)


def sequence_training_contract(member_name: str) -> dict[str, Any]:
    if member_name not in {"obs_decoder_gru", *SEQUENCE_MEMBER_NAMES}:
        raise ValueError(f"unknown S3c GRU-class member: {member_name}")
    return {
        "member": member_name,
        "framework": "torch.nn.GRU",
        "device": "cpu",
        "teacher_forced": True,
        "one_pass_per_user_sequence_per_epoch": True,
        "per_example_prefix_reencoding": False,
        "query_time_single_prefix_encoding": True,
        "shuffle_seed_stream": "baseline_fit",
    }


def _require_member(design: Mapping[str, Any], member: str) -> None:
    if member not in design["battery_membership"]["members"]:
        raise ValueError(f"frozen battery_membership missing {member}")
