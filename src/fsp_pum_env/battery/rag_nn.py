"""S3b retrieval-style prefix-only battery members."""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .base import (
    PrefixEvent,
    Prediction,
    distribution_from_counts,
    event_from_mapping,
    prediction_for_all_actions,
    response_alphabet_size,
)


RETRIEVAL_MEMBER_NAMES = ["rag_k5_episode_retrieval", "nearest_neighbor_user_matching"]


class RagK5EpisodeRetrievalPredictor:
    name = "rag_k5_episode_retrieval"

    def __init__(self, alphabet_size: int, *, k: int = 5):
        self.alphabet_size = int(alphabet_size)
        self.k = int(k)
        self.training_records: list[PrefixEvent] = []
        self._episodes: list[list[PrefixEvent]] = []
        self._current_episode: list[PrefixEvent] = []
        self._action_counts: dict[str, list[float]] = defaultdict(lambda: [0.0] * self.alphabet_size)
        self._global_counts = [0.0] * self.alphabet_size

    @classmethod
    def from_design(cls, design: Mapping[str, Any]) -> "RagK5EpisodeRetrievalPredictor":
        _require_member(design, cls.name)
        return cls(response_alphabet_size(design), k=5)

    def fit(self, records: Iterable[PrefixEvent | Mapping[str, Any]]) -> None:
        self._episodes = []
        self._action_counts.clear()
        self._global_counts = [0.0] * self.alphabet_size
        active: list[PrefixEvent] = []
        for record in records:
            parsed = event_from_mapping(record)
            if parsed.session_boundary == "start" and active:
                self._episodes.append(active)
                active = []
            active.append(parsed)
            symbol = int(parsed.observation["symbol"])
            self._action_counts[parsed.action][symbol] += 1.0
            self._global_counts[symbol] += 1.0
        if active:
            self._episodes.append(active)

    def observe(self, event: PrefixEvent | Mapping[str, Any]) -> None:
        parsed = event_from_mapping(event)
        self.training_records.append(parsed)
        if parsed.session_boundary == "start":
            self._current_episode = []
        self._current_episode.append(parsed)
        self.fit(self.training_records)

    def predict(self, counterfactual_actions: Sequence[str]) -> Prediction:
        if not self._episodes:
            return prediction_for_all_actions(counterfactual_actions, distribution_from_counts(self._global_counts))
        query = _signature(self._current_episode)
        ranked = sorted(
            ((self._episode_distance(query, episode), episode) for episode in self._episodes if len(episode) > len(query)),
            key=lambda item: item[0],
        )[: self.k]
        out: Prediction = {}
        for action in counterfactual_actions:
            counts = [0.0] * self.alphabet_size
            for distance, episode in ranked:
                weight = 1.0 / (1.0 + float(distance))
                for future in episode[len(query) :]:
                    if future.action == str(action):
                        counts[int(future.observation["symbol"])] += weight
                        break
            if sum(counts) <= 0.0:
                counts = self._action_counts.get(str(action), self._global_counts)
            out[str(action)] = distribution_from_counts(counts)
        return out

    @staticmethod
    def _episode_distance(query: tuple[tuple[str, int], ...], episode: Sequence[PrefixEvent]) -> int:
        candidate = _signature(episode[: len(query)])
        mismatches = sum(1 for left, right in zip(query, candidate) if left != right)
        return mismatches + abs(len(query) - len(candidate))


class NearestNeighborUserMatchingPredictor:
    name = "nearest_neighbor_user_matching"

    def __init__(self, alphabet_size: int):
        self.alphabet_size = int(alphabet_size)
        self._users: list[list[PrefixEvent]] = []
        self._prefix: list[PrefixEvent] = []
        self._global_counts = [0.0] * self.alphabet_size

    @classmethod
    def from_design(cls, design: Mapping[str, Any]) -> "NearestNeighborUserMatchingPredictor":
        _require_member(design, cls.name)
        return cls(response_alphabet_size(design))

    @property
    def fitted_user_count(self) -> int:
        return len(self._users)

    def fit(self, records: Iterable[PrefixEvent | Mapping[str, Any]]) -> None:
        self._users = []
        self._global_counts = [0.0] * self.alphabet_size
        active: list[PrefixEvent] = []
        for record in records:
            parsed = event_from_mapping(record)
            if parsed.step_index == 0 and active:
                self._users.append(active)
                active = []
            active.append(parsed)
            self._global_counts[int(parsed.observation["symbol"])] += 1.0
        if active:
            self._users.append(active)

    def observe(self, event: PrefixEvent | Mapping[str, Any]) -> None:
        parsed = event_from_mapping(event)
        if parsed.step_index == 0:
            self._prefix = []
        self._prefix.append(parsed)

    def predict(self, counterfactual_actions: Sequence[str]) -> Prediction:
        if not self._users:
            return prediction_for_all_actions(counterfactual_actions, distribution_from_counts(self._global_counts))
        nearest = min(self._users, key=lambda user: _profile_distance(self._prefix, user))
        action_counts: dict[str, list[float]] = defaultdict(lambda: [0.0] * self.alphabet_size)
        for event in nearest:
            action_counts[event.action][int(event.observation["symbol"])] += 1.0
        out: Prediction = {}
        for action in counterfactual_actions:
            counts = action_counts.get(str(action), self._global_counts)
            out[str(action)] = distribution_from_counts(counts)
        return out


def retrieval_conventions() -> dict[str, dict[str, Any]]:
    return {
        "rag_k5_episode_retrieval": {
            "k": 5,
            "retrieval_unit": "session episode",
            "query": "current session action-symbol prefix",
            "scoring": "weighted nearest-prefix future action lookup",
        },
        "nearest_neighbor_user_matching": {
            "retrieval_unit": "member-view trajectory segmented by step_index reset",
            "query": "current prefix action-symbol profile",
            "scoring": "nearest profile, action-local empirical distribution",
        },
    }


def retrieval_code_hash() -> str:
    h = hashlib.sha256()
    for path in (Path(__file__), Path(__file__).with_name("base.py")):
        h.update(path.name.encode("utf-8"))
        h.update(path.read_bytes())
    return h.hexdigest()


def _signature(events: Sequence[PrefixEvent]) -> tuple[tuple[str, int], ...]:
    return tuple((event.action, int(event.observation["symbol"])) for event in events)


def _profile_distance(left: Sequence[PrefixEvent], right: Sequence[PrefixEvent]) -> int:
    left_counts = Counter(_signature(left))
    right_counts = Counter(_signature(right))
    keys = set(left_counts) | set(right_counts)
    return sum(abs(left_counts[key] - right_counts[key]) for key in keys)


def _require_member(design: Mapping[str, Any], member: str) -> None:
    if member not in design["battery_membership"]["members"]:
        raise ValueError(f"frozen battery_membership missing {member}")
