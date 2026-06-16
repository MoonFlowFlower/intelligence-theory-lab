from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ProbeStep:
    t: int
    action: str
    outcome: float
    latent_at_t: tuple[float, float]
    pe_truth: float


@dataclass(frozen=True)
class Query:
    q_id: str
    query_action: str
    query_context: dict[str, Any]
    truth_outcome: float
    truth_producer: str


@dataclass(frozen=True)
class Episode:
    episode_id: str
    regime: str
    seed: int
    theta: tuple[float, float]
    dynamics_params: dict[str, float]
    probes: tuple[ProbeStep, ...]
    queries: tuple[Query, ...]
    probe_action_set: tuple[str, ...]
    query_action_set: tuple[str, ...]


FIELD_TAGS = {
    "episode_id": {"C", "B"},
    "regime": {"C", "B"},
    "seed": {"C", "B"},
    "t": {"C", "B"},
    "action": {"C", "B"},
    "outcome": {"C", "B"},
    "q_id": {"C", "B"},
    "query_action": {"C", "B"},
    "query_context": {"C", "B"},
    "counterfactual_actions": {"C", "B"},
    "theta": {"H"},
    "dynamics_params": {"H"},
    "latent_at_t": {"H"},
    "pe_truth": {"H", "A"},
    "truth_outcome": {"H", "A", "O"},
    "truth_producer": {"H"},
}


def is_legal_key(key: str) -> bool:
    return bool(FIELD_TAGS.get(key, set()) & {"C", "B"}) and not (
        FIELD_TAGS.get(key, set()) & {"H", "A", "O"}
    )
