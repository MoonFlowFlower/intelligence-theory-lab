"""Prefix-only predictor interface for S3a fair-battery members."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Mapping, Protocol, Sequence


Prediction = dict[str, list[float]]

_FORBIDDEN_PREFIX_KEYS = {
    "theta",
    "z",
    "latent",
    "latents",
    "latent_state",
    "session_state",
    "user_state",
    "trust",
    "seed",
    "rng_seed",
    "future_observation",
    "future_observations",
    "controlled_theta",
    "response_distribution",
}


@dataclass(frozen=True)
class PrefixEvent:
    action: str
    observation: Mapping[str, int]
    session_index: int
    turn_in_session: int
    step_index: int
    session_boundary: str
    extra: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        _reject_forbidden_keys(
            {
                "action": self.action,
                "observation": dict(self.observation),
                "session_index": self.session_index,
                "turn_in_session": self.turn_in_session,
                "step_index": self.step_index,
                "session_boundary": self.session_boundary,
                "extra": self.extra or {},
            }
        )
        if set(self.observation) != {"symbol"}:
            raise ValueError("prefix observation must contain only symbol")
        if not isinstance(self.observation["symbol"], int):
            raise ValueError("prefix observation symbol must be an int")


class PrefixOnlyPredictor(Protocol):
    name: str
    alphabet_size: int

    def observe(self, event: PrefixEvent | Mapping[str, Any]) -> None:
        ...

    def predict(self, counterfactual_actions: Sequence[str]) -> Prediction:
        ...


def load_design(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def event_from_mapping(payload: PrefixEvent | Mapping[str, Any]) -> PrefixEvent:
    if isinstance(payload, PrefixEvent):
        return payload
    return PrefixEvent(
        action=str(payload["action"]),
        observation=payload["observation"],
        session_index=int(payload["session_index"]),
        turn_in_session=int(payload["turn_in_session"]),
        step_index=int(payload["step_index"]),
        session_boundary=str(payload["session_boundary"]),
        extra=payload.get("extra"),
    )


def validate_prediction(prediction: Mapping[str, Sequence[float]], design: Mapping[str, Any], actions: Sequence[str]) -> None:
    alphabet_size = int(design["env_parameters"]["renderer"]["response_alphabet_size"])
    expected_actions = [str(action) for action in actions]
    if set(prediction) != set(expected_actions):
        raise ValueError("prediction must contain exactly the requested counterfactual actions")
    for action in expected_actions:
        distribution = list(prediction[action])
        if len(distribution) != alphabet_size:
            raise ValueError("prediction distribution length does not match frozen response alphabet")
        if any(float(value) < 0.0 for value in distribution):
            raise ValueError("prediction distribution cannot contain negative probabilities")
        if abs(sum(float(value) for value in distribution) - 1.0) > 1e-9:
            raise ValueError("prediction distribution must sum to 1")


def one_hot(alphabet_size: int, symbol: int) -> list[float]:
    if not 0 <= int(symbol) < int(alphabet_size):
        raise ValueError("symbol outside response alphabet")
    out = [0.0] * int(alphabet_size)
    out[int(symbol)] = 1.0
    return out


def uniform(alphabet_size: int) -> list[float]:
    return [1.0 / int(alphabet_size)] * int(alphabet_size)


def distribution_from_counts(counts: Sequence[float], *, empty: str = "uniform") -> list[float]:
    total = float(sum(counts))
    if total <= 0.0:
        if empty == "symbol_zero":
            return one_hot(len(counts), 0)
        return uniform(len(counts))
    return [float(value) / total for value in counts]


def prediction_for_all_actions(actions: Sequence[str], distribution: Sequence[float]) -> Prediction:
    return {str(action): [float(value) for value in distribution] for action in actions}


def frozen_action_list(design: Mapping[str, Any]) -> list[str]:
    action_set = design["env_parameters"]["action_set"]
    return [str(action) for action in action_set["task_actions"]] + [
        str(action) for action in action_set["recommend_actions"]
    ] + [str(item["name"]) for item in action_set["probe_actions"]]


def response_alphabet_size(design: Mapping[str, Any]) -> int:
    return int(design["env_parameters"]["renderer"]["response_alphabet_size"])


def _reject_forbidden_keys(payload: Any) -> None:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            key_lower = str(key).lower()
            if key_lower in _FORBIDDEN_PREFIX_KEYS or any(fragment in key_lower for fragment in ("future", "seed")):
                raise ValueError(f"forbidden prefix key: {key}")
            _reject_forbidden_keys(value)
    elif isinstance(payload, (list, tuple)):
        for value in payload:
            _reject_forbidden_keys(value)
