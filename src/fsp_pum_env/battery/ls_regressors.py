"""Online prefix-only LS-style S3a battery members."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np

from .base import (
    PrefixEvent,
    Prediction,
    event_from_mapping,
    frozen_action_list,
    one_hot,
    prediction_for_all_actions,
    response_alphabet_size,
    uniform,
)


class DiscountedLeastSquaresPredictor:
    name = "discounted_LS_lambda_0.95"

    def __init__(self, alphabet_size: int, actions: Sequence[str], *, discount: float = 0.95):
        self.alphabet_size = int(alphabet_size)
        self.actions = [str(action) for action in actions]
        self.discount = float(discount)
        self._action_index = {action: index for index, action in enumerate(self.actions)}
        self._rows: list[np.ndarray] = []
        self._targets: list[float] = []

    @classmethod
    def from_design(cls, design: Mapping[str, Any]) -> "DiscountedLeastSquaresPredictor":
        if "discounted_LS_lambda_0.95" not in design["battery_membership"]["members"]:
            raise ValueError("frozen battery_membership missing discounted_LS_lambda_0.95")
        return cls(response_alphabet_size(design), frozen_action_list(design), discount=0.95)

    def observe(self, event: PrefixEvent | Mapping[str, Any]) -> None:
        parsed = event_from_mapping(event)
        if parsed.action not in self._action_index:
            return
        self._rows.append(self._features(parsed.action))
        self._targets.append(float(parsed.observation["symbol"]))

    def predict(self, counterfactual_actions: Sequence[str]) -> Prediction:
        if not self._rows:
            return prediction_for_all_actions(counterfactual_actions, uniform(self.alphabet_size))
        beta = self._fit()
        out: Prediction = {}
        for action in counterfactual_actions:
            value = float(self._features(str(action)) @ beta)
            symbol = int(round(min(max(value, 0.0), self.alphabet_size - 1)))
            out[str(action)] = one_hot(self.alphabet_size, symbol)
        return out

    def _fit(self) -> np.ndarray:
        x = np.vstack(self._rows)
        y = np.asarray(self._targets, dtype=float)
        powers = np.arange(len(y) - 1, -1, -1, dtype=float)
        weights = np.power(self.discount, powers)
        wx = x * np.sqrt(weights).reshape(-1, 1)
        wy = y * np.sqrt(weights)
        beta, *_ = np.linalg.lstsq(wx, wy, rcond=None)
        return beta

    def _features(self, action: str) -> np.ndarray:
        features = np.zeros(len(self.actions) + 1, dtype=float)
        features[0] = 1.0
        index = self._action_index.get(action)
        if index is not None:
            features[index + 1] = 1.0
        return features


class RunningAveragePreferenceRegressor:
    name = "running_average_preference_regressor"

    def __init__(self, alphabet_size: int, actions: Sequence[str]):
        self.alphabet_size = int(alphabet_size)
        self.actions = [str(action) for action in actions]
        self._sums = {action: 0.0 for action in self.actions}
        self._counts = {action: 0 for action in self.actions}
        self._global_sum = 0.0
        self._global_count = 0

    @classmethod
    def from_design(cls, design: Mapping[str, Any]) -> "RunningAveragePreferenceRegressor":
        if "running_average_preference_regressor" not in design["battery_membership"]["members"]:
            raise ValueError("frozen battery_membership missing running_average_preference_regressor")
        return cls(response_alphabet_size(design), frozen_action_list(design))

    def observe(self, event: PrefixEvent | Mapping[str, Any]) -> None:
        parsed = event_from_mapping(event)
        symbol = float(parsed.observation["symbol"])
        self._global_sum += symbol
        self._global_count += 1
        if parsed.action in self._counts:
            self._sums[parsed.action] += symbol
            self._counts[parsed.action] += 1

    def predict(self, counterfactual_actions: Sequence[str]) -> Prediction:
        out: Prediction = {}
        for action in counterfactual_actions:
            action = str(action)
            if self._counts.get(action, 0) > 0:
                value = self._sums[action] / self._counts[action]
            elif self._global_count > 0:
                value = self._global_sum / self._global_count
            else:
                value = 0.0
            symbol = int(round(min(max(value, 0.0), self.alphabet_size - 1)))
            out[action] = one_hot(self.alphabet_size, symbol)
        return out
