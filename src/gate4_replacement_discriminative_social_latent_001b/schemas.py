from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


FORBIDDEN_DECISION_FIELDS = {
    "seed",
    "seed_id",
    "context_id",
    "partner_id",
    "phase_token",
    "split_label",
    "oracle_latent_label",
    "artifact_path",
    "bundle_path",
    "answer_key",
    "future_outcome",
}


def _reject_forbidden(payload: dict[str, Any]) -> None:
    present = sorted(FORBIDDEN_DECISION_FIELDS.intersection(payload))
    if present:
        raise ValueError(f"forbidden decision fields present: {', '.join(present)}")


@dataclass(frozen=True)
class Observation:
    observable_partner: str
    observable_context: str
    prompt_features: dict[str, Any]
    legal_history: list[dict[str, Any]] = field(default_factory=list)

    def to_json_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        _reject_forbidden(payload)
        return payload

    @classmethod
    def from_json_dict(cls, payload: dict[str, Any]) -> "Observation":
        _reject_forbidden(payload)
        return cls(
            observable_partner=str(payload["observable_partner"]),
            observable_context=str(payload["observable_context"]),
            prompt_features=dict(payload.get("prompt_features", {})),
            legal_history=list(payload.get("legal_history", [])),
        )


@dataclass(frozen=True)
class Action:
    action_type: str
    value: str
    confidence: float

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_json_dict(cls, payload: dict[str, Any]) -> "Action":
        return cls(
            action_type=str(payload["action_type"]),
            value=str(payload["value"]),
            confidence=float(payload["confidence"]),
        )


@dataclass(frozen=True)
class Feedback:
    feedback_type: str
    value: str

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_json_dict(cls, payload: dict[str, Any]) -> "Feedback":
        return cls(feedback_type=str(payload["feedback_type"]), value=str(payload["value"]))


@dataclass(frozen=True)
class CandidateState:
    beliefs: dict[str, str] = field(default_factory=dict)
    uncertainty: dict[str, float] = field(default_factory=dict)
    memory_write_count: int = 0
    memory_read_count: int = 0

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_json_dict(cls, payload: dict[str, Any]) -> "CandidateState":
        return cls(
            beliefs=dict(payload.get("beliefs", {})),
            uncertainty={str(k): float(v) for k, v in payload.get("uncertainty", {}).items()},
            memory_write_count=int(payload.get("memory_write_count", 0)),
            memory_read_count=int(payload.get("memory_read_count", 0)),
        )


@dataclass(frozen=True)
class EpisodeRecord:
    episode_id: str
    seed_id: str
    split_family: str
    context_id: str
    partner_id: str
    train_context_id: str
    heldout_context_id: str
    target_action: str
    query_feedback: str
    counterfactual_feedback: str
    counterfactual_pair_id: str | None
    remapped_episode_id: str | None
    observation: Observation

    def to_json_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["observation"] = self.observation.to_json_dict()
        return payload

    @classmethod
    def from_json_dict(cls, payload: dict[str, Any]) -> "EpisodeRecord":
        row = dict(payload)
        row["observation"] = Observation.from_json_dict(row["observation"])
        return cls(**row)


@dataclass(frozen=True)
class ProvenanceRecord:
    result_family: str
    producer_function: str
    input_artifacts: list[str]
    run_id: str
    seed_ids: list[str]
    context_ids: list[str]
    partner_ids: list[str]
    episode_ids: list[str]
    split_id: str
    aggregation_rule: str
    code_path_hash: str
    candidate_or_baseline_id: str | None = None
    intervention_id: str | None = None
    baseline_invocation_path: str | None = None
    ablation_invocation_path: str | None = None
    leakage_scanner_path: str | None = None
    replay_recompute_path: str | None = None
    budget_parity_producer_path: str | None = None
    created_at: str = "2026-06-13T00:00:00Z"
    static_score_injection: bool = False

    def to_json_dict(self) -> dict[str, Any]:
        return asdict(self)

