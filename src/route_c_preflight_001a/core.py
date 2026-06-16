from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import math
import random
from typing import Any, Iterable

from . import CLAIM_CEILING
from . import provenance


@dataclass(frozen=True)
class Config:
    n_channels: int = 8
    k_self: int = 3
    m_confounder: int = 2
    gain: float = 2.0
    noise_sd: float = 0.15
    n_passive: int = 32
    interventions_per_channel: int = 12
    confounder_strength: float = 1.0
    permute_channels: bool = True
    premise_band: float = 0.12
    headroom_band: float = 0.25

    @property
    def chance(self) -> float:
        return self.k_self / self.n_channels

    @property
    def premise_threshold(self) -> float:
        return self.chance + self.premise_band

    def public(self) -> dict[str, Any]:
        return {
            "n_channels": self.n_channels,
            "k_self": self.k_self,
            "n_passive": self.n_passive,
            "interventions_per_channel": self.interventions_per_channel,
            "premise_threshold": self.premise_threshold,
            "headroom_band": self.headroom_band,
            "claim_ceiling": CLAIM_CEILING,
        }


@dataclass(frozen=True)
class HiddenEpisode:
    episode_id: str
    seed: int
    config: Config
    self_set_original: frozenset[int]
    weights: tuple[tuple[float, ...], ...]
    public_order: tuple[int, ...]
    handles_by_original: tuple[str, ...]
    learner_observed_seed: int

    @property
    def handles(self) -> list[str]:
        return [self.handles_by_original[original] for original in self.public_order]

    @property
    def truth_self_handles(self) -> list[str]:
        return sorted(self.handles_by_original[index] for index in self.self_set_original)

    @property
    def original_by_handle(self) -> dict[str, int]:
        return {handle: original for original, handle in enumerate(self.handles_by_original)}


def default_config(**overrides: Any) -> Config:
    return replace(Config(), **overrides)


def _dot(left: Iterable[float], right: Iterable[float]) -> float:
    return sum(a * b for a, b in zip(left, right))


def _handle_token(seed: int, public_position: int) -> str:
    token = provenance.sha256_text(f"route-c-handle:{seed}:{public_position}")[:10]
    return f"h_{token}"


def sample_episode(seed: int, config: Config) -> HiddenEpisode:
    if not 0 < config.k_self < config.n_channels:
        raise ValueError("k_self must satisfy 0 < k_self < n_channels")
    rng = random.Random(seed)
    self_set = frozenset(rng.sample(range(config.n_channels), config.k_self))
    weights = tuple(
        tuple(rng.gauss(0.0, config.confounder_strength) for _ in range(config.m_confounder))
        for _ in range(config.n_channels)
    )
    public_order = list(range(config.n_channels))
    if config.permute_channels:
        rng.shuffle(public_order)
    handles_by_original = [""] * config.n_channels
    for public_position, original in enumerate(public_order):
        handles_by_original[original] = _handle_token(seed, public_position)
    return HiddenEpisode(
        episode_id=f"route-c-episode-{seed}",
        seed=seed,
        config=config,
        self_set_original=self_set,
        weights=weights,
        public_order=tuple(public_order),
        handles_by_original=tuple(handles_by_original),
        learner_observed_seed=seed + 10_000_000,
    )


def _row_values(episode: HiddenEpisode, rng: random.Random) -> dict[str, float]:
    confounder = [rng.gauss(0.0, 1.0) for _ in range(episode.config.m_confounder)]
    values = {}
    for original in range(episode.config.n_channels):
        values[episode.handles_by_original[original]] = _dot(episode.weights[original], confounder) + rng.gauss(
            0.0, episode.config.noise_sd
        )
    return values


def generate_passive_observations(episode: HiddenEpisode) -> list[dict[str, Any]]:
    rng = random.Random(episode.seed * 3571 + 11)
    rows = []
    for index in range(episode.config.n_passive):
        rows.append(
            {
                "row_id": f"{episode.episode_id}-passive-{index}",
                "regime": "passive",
                "handle_values": _row_values(episode, rng),
                "metadata": {},
            }
        )
    return rows


def generate_intervention_log(episode: HiddenEpisode) -> list[dict[str, Any]]:
    rng = random.Random(episode.seed * 7919 + 17)
    rows = []
    for handle in episode.handles:
        original = episode.original_by_handle[handle]
        for repeat in range(episode.config.interventions_per_channel):
            value = -1.0 if rng.random() < 0.5 else 1.0
            post_values = _row_values(episode, rng)
            if original in episode.self_set_original:
                post_values[handle] += episode.config.gain * value
            rows.append(
                {
                    "row_id": f"{episode.episode_id}-do-{handle}-{repeat}",
                    "episode_id": episode.episode_id,
                    "regime": "interventional",
                    "target_handle": handle,
                    "value": value,
                    "post_handle_values": post_values,
                    "metadata": {},
                }
            )
    return rows


def legal_view_for_episode(episode: HiddenEpisode, *, include_interventions: bool) -> dict[str, Any]:
    return {
        "episode_id": episode.episode_id,
        "seed": episode.seed,
        "learner_observed_seed": episode.learner_observed_seed,
        "handles": episode.handles,
        "public_config": episode.config.public(),
        "passive_rows": generate_passive_observations(episode),
        "intervention_log": generate_intervention_log(episode) if include_interventions else [],
        "query": {"handles": episode.handles, "k_self": episode.config.k_self},
    }


def build_episode_bundle(*, seeds: Iterable[int], config: Config, run_id: str) -> dict[str, Any]:
    episodes = []
    for seed in seeds:
        hidden = sample_episode(int(seed), config)
        episodes.append(
            {
                "episode_id": hidden.episode_id,
                "seed": hidden.seed,
                "legal": legal_view_for_episode(hidden, include_interventions=False),
                "interventional_legal": legal_view_for_episode(hidden, include_interventions=True),
                "truth_self_handles": hidden.truth_self_handles,
                "truth_seed": hidden.seed,
                "learner_observed_seed": hidden.learner_observed_seed,
                "public_order_handles": hidden.handles,
            }
        )
    return {
        "producer_function": provenance.producer_name(build_episode_bundle),
        "run_id": run_id,
        "config": asdict(config),
        "episodes": episodes,
        "claim_ceiling": CLAIM_CEILING,
    }


def score_self_set_prediction(predicted: Iterable[str], truth: Iterable[str], *, k_self: int) -> float:
    predicted_set = set(predicted)
    truth_set = set(truth)
    return len(predicted_set & truth_set) / k_self


def _predict_from_membership_map(legal: dict[str, Any], membership_key: str) -> list[str] | None:
    mapping = legal.get(membership_key)
    if isinstance(mapping, dict):
        return sorted([handle for handle, is_member in mapping.items() if is_member])[: legal["query"]["k_self"]]
    return None


def obs_only_baseline(legal_episodes: list[dict[str, Any]], *, run_id: str) -> dict[str, Any]:
    predictions = []
    for legal in legal_episodes:
        if legal.get("intervention_log"):
            raise ValueError("obs_only_baseline_received_intervention_data")
        predicted = (
            _predict_from_membership_map(legal, "leaked_self_membership_by_handle")
            or _predict_from_membership_map(legal, "confounder_self_membership_by_handle")
            or legal["handles"][: legal["query"]["k_self"]]
        )
        predictions.append(
            {
                "episode_id": legal["episode_id"],
                "predicted_self_handles": sorted(predicted),
                "producer_function": provenance.producer_name(obs_only_baseline),
            }
        )
    return {"producer_function": provenance.producer_name(obs_only_baseline), "run_id": run_id, "predictions": predictions}


def schema_only_attacker(legal_episodes: list[dict[str, Any]], *, run_id: str) -> dict[str, Any]:
    predictions = []
    for legal in legal_episodes:
        aliases = legal.get("schema_alias_by_handle", {})
        leaked = [handle for handle, alias in aliases.items() if "self" in str(alias).lower() or "target" in str(alias).lower()]
        predicted = sorted(leaked)[: legal["query"]["k_self"]] if leaked else []
        predictions.append(
            {
                "episode_id": legal["episode_id"],
                "predicted_self_handles": sorted(predicted),
                "producer_function": provenance.producer_name(schema_only_attacker),
            }
        )
    return {"producer_function": provenance.producer_name(schema_only_attacker), "run_id": run_id, "predictions": predictions}


def name_order_attacker(legal_episodes: list[dict[str, Any]], *, run_id: str) -> dict[str, Any]:
    predictions = []
    for legal in legal_episodes:
        aliases = legal.get("schema_alias_by_handle", {})
        leaked = [handle for handle, alias in aliases.items() if str(alias).startswith("self_")]
        if not leaked:
            leaked = [handle for handle in legal["handles"] if "self" in handle.lower() or "target" in handle.lower()]
        predicted = sorted(leaked)[: legal["query"]["k_self"]] if leaked else []
        predictions.append(
            {
                "episode_id": legal["episode_id"],
                "predicted_self_handles": sorted(predicted),
                "producer_function": provenance.producer_name(name_order_attacker),
            }
        )
    return {"producer_function": provenance.producer_name(name_order_attacker), "run_id": run_id, "predictions": predictions}


def _score_predictions(
    *,
    bundle: dict[str, Any],
    prediction_report: dict[str, Any],
    producer_function: Any,
    run_id: str,
    config: Config,
) -> dict[str, Any]:
    truth_by_episode = {episode["episode_id"]: episode["truth_self_handles"] for episode in bundle["episodes"]}
    per_episode = []
    scores = []
    for prediction in prediction_report["predictions"]:
        episode_id = prediction["episode_id"]
        score = score_self_set_prediction(
            prediction["predicted_self_handles"],
            truth_by_episode[episode_id],
            k_self=config.k_self,
        )
        scores.append(score)
        per_episode.append(
            {
                "episode_id": episode_id,
                "predicted_self_handles": prediction["predicted_self_handles"],
                "score": round(score, 6),
            }
        )
    aggregate = provenance.aggregate_score_record(
        scores=scores,
        producer_function=producer_function,
        inputs={"episode_count": len(scores), "config_hash": provenance.sha256_json(bundle["config"])},
        run_id=run_id,
        episode_ids=[row["episode_id"] for row in per_episode],
        threshold_used=config.premise_threshold,
    )
    return {**prediction_report, "per_episode": per_episode, "aggregate_score": aggregate}


def run_baseline_panel(bundle: dict[str, Any], *, run_id: str) -> dict[str, Any]:
    config = Config(**bundle["config"])
    legal = [episode["legal"] for episode in bundle["episodes"]]
    obs = _score_predictions(
        bundle=bundle,
        prediction_report=obs_only_baseline(legal, run_id=f"{run_id}-obs-only"),
        producer_function=obs_only_baseline,
        run_id=f"{run_id}-obs-only-score",
        config=config,
    )
    schema = _score_predictions(
        bundle=bundle,
        prediction_report=schema_only_attacker(legal, run_id=f"{run_id}-schema"),
        producer_function=schema_only_attacker,
        run_id=f"{run_id}-schema-score",
        config=config,
    )
    name = _score_predictions(
        bundle=bundle,
        prediction_report=name_order_attacker(legal, run_id=f"{run_id}-name-order"),
        producer_function=name_order_attacker,
        run_id=f"{run_id}-name-order-score",
        config=config,
    )
    return {
        "producer_function": provenance.producer_name(run_baseline_panel),
        "run_id": run_id,
        "obs_only": obs,
        "schema_only": schema,
        "name_order": name,
        "baseline_received_intervention_data": False,
    }


def non_identifiability_premise_gate(panel: dict[str, Any], *, config: Config) -> dict[str, Any]:
    obs = panel["obs_only"]["aggregate_score"]["value"]
    schema = panel["schema_only"]["aggregate_score"]["value"]
    name = panel["name_order"]["aggregate_score"]["value"]
    threshold = config.premise_threshold
    if schema > threshold or name > threshold:
        return _gate_verdict("blocked_by_schema_alias_leakage", max(schema, name), threshold, False)
    if obs > threshold:
        return _gate_verdict("blocked_by_observation_decodable_self_set", obs, threshold, False)
    return _gate_verdict("non_identifiability_present", obs, threshold, True)


def _gate_verdict(verdict: str, value: float, threshold: float, passed: bool) -> dict[str, Any]:
    return {
        "producer_function": provenance.producer_name(_gate_verdict),
        "verdict": verdict,
        "value": round(float(value), 6),
        "threshold": round(float(threshold), 6),
        "passed": passed,
        "failure_path_available": True,
    }


def _predict_oracle_for_legal(legal: dict[str, Any]) -> tuple[list[str], dict[str, dict[str, float]]]:
    effect_sums = {handle: 0.0 for handle in legal["handles"]}
    effect_weights = {handle: 0.0 for handle in legal["handles"]}
    for row in legal["intervention_log"]:
        handle = row["target_handle"]
        value = float(row["value"])
        effect_sums[handle] += value * float(row["post_handle_values"][handle])
        effect_weights[handle] += value * value
    effects = {
        handle: (effect_sums[handle] / effect_weights[handle] if effect_weights[handle] else 0.0)
        for handle in legal["handles"]
    }
    ranked = sorted(legal["handles"], key=lambda handle: (-abs(effects[handle]), handle))
    return sorted(ranked[: legal["query"]["k_self"]]), {
        "effect_sums": effect_sums,
        "effect_weights": effect_weights,
        "effects": effects,
    }


def run_interventional_oracle(bundle: dict[str, Any], *, run_id: str) -> dict[str, Any]:
    config = Config(**bundle["config"])
    per_episode = []
    scores = []
    predictions = []
    legal_rows = []
    serialized_state = {"episodes": {}}
    for episode in bundle["episodes"]:
        legal = episode["interventional_legal"]
        predicted, effect_state = _predict_oracle_for_legal(legal)
        score = score_self_set_prediction(predicted, episode["truth_self_handles"], k_self=config.k_self)
        scores.append(score)
        per_episode.append({"episode_id": episode["episode_id"], "predicted_self_handles": predicted, "score": round(score, 6)})
        prediction_hash = provenance.sha256_json({"episode_id": episode["episode_id"], "predicted_self_handles": predicted})
        predictions.append(
            {
                "episode_id": episode["episode_id"],
                "predicted_self_handles": predicted,
                "prediction_hash": prediction_hash,
            }
        )
        serialized_state["episodes"][episode["episode_id"]] = {
            "handles": legal["handles"],
            "k_self": legal["query"]["k_self"],
            "effect_state": effect_state,
        }
        for row in legal["intervention_log"]:
            legal_rows.append(row)
    aggregate = provenance.aggregate_score_record(
        scores=scores,
        producer_function=run_interventional_oracle,
        inputs={"episode_count": len(scores), "config_hash": provenance.sha256_json(bundle["config"])},
        run_id=run_id,
        episode_ids=[row["episode_id"] for row in per_episode],
        threshold_used=config.premise_threshold,
    )
    return {
        "producer_function": provenance.producer_name(run_interventional_oracle),
        "run_id": run_id,
        "used_randomized_interventions": True,
        "baseline_accessed_intervention_data": False,
        "per_episode": per_episode,
        "aggregate_score": aggregate,
        "serialized_state": serialized_state,
        "legal_intervention_rows": legal_rows,
        "predictions": predictions,
    }


def interventional_headroom_gate(*, obs_score: float, oracle_score: float, config: Config) -> dict[str, Any]:
    delta = oracle_score - obs_score
    if delta > config.headroom_band:
        return _gate_verdict("interventional_headroom_present", delta, config.headroom_band, True)
    return _gate_verdict("blocked_by_no_interventional_headroom", delta, config.headroom_band, False)


def trace_rows(bundle: dict[str, Any], panel: dict[str, Any], oracle: dict[str, Any]) -> list[dict[str, Any]]:
    obs_by_episode = {row["episode_id"]: row for row in panel["obs_only"]["per_episode"]}
    schema_by_episode = {row["episode_id"]: row for row in panel["schema_only"]["per_episode"]}
    name_by_episode = {row["episode_id"]: row for row in panel["name_order"]["per_episode"]}
    oracle_by_episode = {row["episode_id"]: row for row in oracle["per_episode"]}
    rows = []
    for episode in bundle["episodes"]:
        episode_id = episode["episode_id"]
        rows.append(
            {
                "run_id": bundle["run_id"],
                "seed": episode["seed"],
                "episode_id": episode_id,
                "producer_function": provenance.producer_name(trace_rows),
                "truth_self_handles_oracle_side": episode["truth_self_handles"],
                "obs_only": obs_by_episode[episode_id],
                "schema_only": schema_by_episode[episode_id],
                "name_order": name_by_episode[episode_id],
                "interventional_oracle": oracle_by_episode[episode_id],
                "claim_ceiling": CLAIM_CEILING,
            }
        )
    return rows
