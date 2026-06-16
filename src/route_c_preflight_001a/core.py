from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import math
import random
from typing import Any, Callable, Iterable

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


# --------------------------------------------------------------------------- #
# Generator (unchanged semantics: S never enters the passive law by construction)
# --------------------------------------------------------------------------- #
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


# --------------------------------------------------------------------------- #
# Passive value access + math helpers (pure Python, deterministic)
# --------------------------------------------------------------------------- #
def passive_value_matrix(legal: dict[str, Any]) -> tuple[list[str], list[list[float]]]:
    """Return (handles, rows) read ONLY from legal['passive_rows'][*]['handle_values'].

    This is the sole passive-value entry point used by the value-level attacker
    family; it touches no key/label/name/answer field.
    """
    handles = list(legal["handles"])
    rows: list[list[float]] = []
    for row in legal.get("passive_rows", []):
        values = row["handle_values"]
        rows.append([float(values[handle]) for handle in handles])
    return handles, rows


def _column(rows: list[list[float]], j: int) -> list[float]:
    return [row[j] for row in rows]


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _variance(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mu = _mean(values)
    return sum((v - mu) ** 2 for v in values) / (len(values) - 1)


def _covariance_matrix(rows: list[list[float]], n: int) -> list[list[float]]:
    if len(rows) < 2:
        return [[0.0] * n for _ in range(n)]
    means = [_mean(_column(rows, j)) for j in range(n)]
    cov = [[0.0] * n for _ in range(n)]
    denom = len(rows) - 1
    for a in range(n):
        for b in range(a, n):
            s = 0.0
            for row in rows:
                s += (row[a] - means[a]) * (row[b] - means[b])
            cov[a][b] = cov[b][a] = s / denom
    return cov


def _top_eigenvector(matrix: list[list[float]], n: int, *, iterations: int = 64) -> list[float]:
    """Deterministic power iteration from a fixed start vector."""
    vec = [1.0 / math.sqrt(n)] * n
    for _ in range(iterations):
        nxt = [0.0] * n
        for a in range(n):
            row = matrix[a]
            nxt[a] = sum(row[b] * vec[b] for b in range(n))
        norm = math.sqrt(sum(x * x for x in nxt))
        if norm == 0.0:
            return vec
        vec = [x / norm for x in nxt]
    return vec


def _topk_by_score(handles: list[str], scores: dict[str, float], k: int) -> list[str]:
    """Top-k handles by score; deterministic tie-break by handle string."""
    ranked = sorted(handles, key=lambda h: (-scores[h], h))
    return sorted(ranked[:k])


# --------------------------------------------------------------------------- #
# Passive observational attacker family (6.1: "may use any observational
# structure (covariance, clustering, supervised fit on passive features)")
# Each attacker maps a list of legal views -> list of predicted handle lists.
# --------------------------------------------------------------------------- #
def positional_first_k_attacker(legal_episodes: list[dict[str, Any]], *, config: Config) -> list[list[str]]:
    """Weak diagnostic only. Reads no values; first-k handles. Kept to show that
    a positional no-op stays at chance and cannot, alone, decode a value leak."""
    out = []
    for legal in legal_episodes:
        out.append(sorted(legal["handles"][: legal["query"]["k_self"]]))
    return out


def passive_mean_attacker(legal_episodes: list[dict[str, Any]], *, config: Config) -> list[list[str]]:
    out = []
    for legal in legal_episodes:
        handles, rows = passive_value_matrix(legal)
        scores = {h: abs(_mean(_column(rows, j))) for j, h in enumerate(handles)}
        out.append(_topk_by_score(handles, scores, legal["query"]["k_self"]))
    return out


def passive_variance_attacker(legal_episodes: list[dict[str, Any]], *, config: Config) -> list[list[str]]:
    out = []
    for legal in legal_episodes:
        handles, rows = passive_value_matrix(legal)
        scores = {h: _variance(_column(rows, j)) for j, h in enumerate(handles)}
        out.append(_topk_by_score(handles, scores, legal["query"]["k_self"]))
    return out


def passive_correlation_attacker(legal_episodes: list[dict[str, Any]], *, config: Config) -> list[list[str]]:
    """Rank handles by aggregate absolute correlation with the other channels."""
    out = []
    for legal in legal_episodes:
        handles, rows = passive_value_matrix(legal)
        n = len(handles)
        cov = _covariance_matrix(rows, n)
        sd = [math.sqrt(cov[j][j]) if cov[j][j] > 0 else 0.0 for j in range(n)]
        scores = {}
        for a, h in enumerate(handles):
            total = 0.0
            for b in range(n):
                if b == a:
                    continue
                denom = sd[a] * sd[b]
                total += abs(cov[a][b] / denom) if denom > 0 else 0.0
            scores[h] = total
        out.append(_topk_by_score(handles, scores, legal["query"]["k_self"]))
    return out


def passive_pca_subspace_attacker(legal_episodes: list[dict[str, Any]], *, config: Config) -> list[list[str]]:
    """Rank handles by squared loading on the top passive principal component."""
    out = []
    for legal in legal_episodes:
        handles, rows = passive_value_matrix(legal)
        n = len(handles)
        cov = _covariance_matrix(rows, n)
        top = _top_eigenvector(cov, n)
        scores = {h: top[j] * top[j] for j, h in enumerate(handles)}
        out.append(_topk_by_score(handles, scores, legal["query"]["k_self"]))
    return out


def _channel_mean_feature(legal: dict[str, Any]) -> dict[str, float]:
    handles, rows = passive_value_matrix(legal)
    return {h: _mean(_column(rows, j)) for j, h in enumerate(handles)}


def passive_cross_episode_attacker(legal_episodes: list[dict[str, Any]], *, config: Config) -> list[list[str]]:
    """Population attacker: pool per-channel mean across all episodes, then within
    each episode rank channels by |z-score| of their mean vs the pooled
    distribution. A value-level mean shift on self channels makes them outliers;
    on clean data the pooled mean is S-independent -> chance. Reads no truth."""
    per_episode_means = [_channel_mean_feature(legal) for legal in legal_episodes]
    pooled = [m for means in per_episode_means for m in means.values()]
    mu = _mean(pooled)
    sd = math.sqrt(_variance(pooled)) if len(pooled) > 1 else 0.0
    out = []
    for legal, means in zip(legal_episodes, per_episode_means):
        if sd > 0:
            scores = {h: abs((means[h] - mu) / sd) for h in means}
        else:
            scores = {h: 0.0 for h in means}
        out.append(_topk_by_score(list(means), scores, legal["query"]["k_self"]))
    return out


# Training-seed range for the supervised attacker. Disjoint from any evaluation
# seed range used in this lab and from the learner_observed_seed offset
# (seed + 10_000_000), so the trainer never reuses an evaluation episode.
SUPERVISED_TRAIN_SEEDS = tuple(range(90_000_000, 90_000_048))


def _channel_features(legal: dict[str, Any]) -> dict[str, list[float]]:
    handles, rows = passive_value_matrix(legal)
    n = len(handles)
    cov = _covariance_matrix(rows, n)
    top = _top_eigenvector(cov, n)
    sd = [math.sqrt(cov[j][j]) if cov[j][j] > 0 else 0.0 for j in range(n)]
    feats: dict[str, list[float]] = {}
    for j, h in enumerate(handles):
        col = _column(rows, j)
        corr = 0.0
        for b in range(n):
            if b == j:
                continue
            denom = sd[j] * sd[b]
            corr += abs(cov[j][b] / denom) if denom > 0 else 0.0
        feats[h] = [abs(_mean(col)), _variance(col), corr, top[j] * top[j]]
    return feats


def supervised_passive_feature_attacker(legal_episodes: list[dict[str, Any]], *, config: Config) -> list[list[str]]:
    """Split-safe supervised fit on passive features.

    Trains a nearest-centroid linear discriminant on DISJOINT training episodes
    (truth legally assigned by the trainer to its own generated episodes), then
    evaluates on the supplied (held-out) episodes using passive features ONLY.
    Evaluation truth is never accessed (the legal views carry no truth field).
    Because S is absent from the passive law, the learned weights generalise to
    chance on clean data by construction.
    """
    train_config = replace(config, gain=0.0)  # passive features do not depend on gain
    self_feats: list[list[float]] = []
    other_feats: list[list[float]] = []
    eval_seeds = {int(le.get("seed")) for le in legal_episodes if le.get("seed") is not None}
    for seed in SUPERVISED_TRAIN_SEEDS:
        if seed in eval_seeds:
            continue  # split-safety guard: never train on an eval seed
        episode = sample_episode(seed, train_config)
        legal = legal_view_for_episode(episode, include_interventions=False)
        truth = set(episode.truth_self_handles)  # legal: trainer's own episode
        feats = _channel_features(legal)
        for handle, vector in feats.items():
            (self_feats if handle in truth else other_feats).append(vector)

    if not self_feats or not other_feats:
        # Cannot fit -> fall back to chance-equivalent positional guess.
        return positional_first_k_attacker(legal_episodes, config=config)

    dim = len(self_feats[0])
    all_feats = self_feats + other_feats
    f_mean = [_mean([row[d] for row in all_feats]) for d in range(dim)]
    f_sd = [math.sqrt(_variance([row[d] for row in all_feats])) or 1.0 for d in range(dim)]

    def standardize(vec: list[float]) -> list[float]:
        return [(vec[d] - f_mean[d]) / f_sd[d] for d in range(dim)]

    self_centroid = [_mean([standardize(r)[d] for r in self_feats]) for d in range(dim)]
    other_centroid = [_mean([standardize(r)[d] for r in other_feats]) for d in range(dim)]
    weight = [self_centroid[d] - other_centroid[d] for d in range(dim)]

    out = []
    for legal in legal_episodes:
        feats = _channel_features(legal)
        scores = {h: _dot(weight, standardize(vec)) for h, vec in feats.items()}
        out.append(_topk_by_score(list(feats), scores, legal["query"]["k_self"]))
    return out


def legal_field_membership_attacker(legal_episodes: list[dict[str, Any]], *, config: Config) -> list[list[str]]:
    """Reads an explicit membership/answer map IF the schema leaks one (L1/L5).
    On clean data no such field exists -> emits an empty prediction (contributes
    nothing to the family max). This is the answer-map reader the blueprint
    requires to remain 'in addition' to the value-level attackers."""
    out = []
    for legal in legal_episodes:
        prediction: list[str] = []
        for key in ("leaked_self_membership_by_handle", "confounder_self_membership_by_handle"):
            mapping = legal.get(key)
            if isinstance(mapping, dict):
                prediction = sorted([h for h, member in mapping.items() if member])[: legal["query"]["k_self"]]
                break
        out.append(sorted(prediction))
    return out


# (name, function, value_level, weak)
PASSIVE_ATTACKER_FAMILY: tuple[tuple[str, Callable[..., Any], bool, bool], ...] = (
    ("positional_first_k_attacker", positional_first_k_attacker, False, True),
    ("passive_mean_attacker", passive_mean_attacker, True, False),
    ("passive_variance_attacker", passive_variance_attacker, True, False),
    ("passive_correlation_attacker", passive_correlation_attacker, True, False),
    ("passive_pca_subspace_attacker", passive_pca_subspace_attacker, True, False),
    ("passive_cross_episode_attacker", passive_cross_episode_attacker, True, False),
    ("supervised_passive_feature_attacker", supervised_passive_feature_attacker, True, False),
    ("legal_field_membership_attacker", legal_field_membership_attacker, False, False),
)


def obs_only_baseline(legal_episodes: list[dict[str, Any]], *, run_id: str, config: Config | None = None) -> dict[str, Any]:
    """Run the passive observational attacker family.

    Guards against interventional contamination (obs-only must never see do-data),
    then returns per-attacker predictions. Scoring + family-max is done by
    `run_obs_only_family`.
    """
    for legal in legal_episodes:
        if legal.get("intervention_log"):
            raise ValueError("obs_only_baseline_received_intervention_data")
    config = config or default_config()
    attackers: dict[str, Any] = {}
    for name, fn, value_level, weak in PASSIVE_ATTACKER_FAMILY:
        predictions = fn(legal_episodes, config=config)
        attackers[name] = {
            "producer_function": provenance.producer_name(fn),
            "value_level": value_level,
            "weak_diagnostic": weak,
            "predictions": [
                {"episode_id": legal["episode_id"], "predicted_self_handles": sorted(pred)}
                for legal, pred in zip(legal_episodes, predictions)
            ],
        }
    return {
        "producer_function": provenance.producer_name(obs_only_baseline),
        "run_id": run_id,
        "attackers": attackers,
    }


def schema_only_attacker(legal_episodes: list[dict[str, Any]], *, config: Config | None = None) -> list[list[str]]:
    out = []
    for legal in legal_episodes:
        aliases = legal.get("schema_alias_by_handle", {})
        leaked = [h for h, alias in aliases.items() if "self" in str(alias).lower() or "target" in str(alias).lower()]
        out.append(sorted(leaked)[: legal["query"]["k_self"]] if leaked else [])
    return out


def name_order_attacker(legal_episodes: list[dict[str, Any]], *, config: Config | None = None) -> list[list[str]]:
    out = []
    for legal in legal_episodes:
        aliases = legal.get("schema_alias_by_handle", {})
        leaked = [h for h, alias in aliases.items() if str(alias).startswith("self_")]
        if not leaked:
            leaked = [h for h in legal["handles"] if "self" in h.lower() or "target" in h.lower()]
        out.append(sorted(leaked)[: legal["query"]["k_self"]] if leaked else [])
    return out


# --------------------------------------------------------------------------- #
# Scoring + provenance plumbing
# --------------------------------------------------------------------------- #
def _score_attacker(
    *,
    bundle: dict[str, Any],
    legal_episodes: list[dict[str, Any]],
    predictions: list[dict[str, Any]],
    producer_function: Callable[..., Any],
    run_id: str,
    config: Config,
    subsystem: str,
    threshold_snapshot_hash: str,
) -> dict[str, Any]:
    truth_by_episode = {e["episode_id"]: e["truth_self_handles"] for e in bundle["episodes"]}
    per_episode = []
    scores = []
    for prediction in predictions:
        episode_id = prediction["episode_id"]
        score = score_self_set_prediction(
            prediction["predicted_self_handles"], truth_by_episode[episode_id], k_self=config.k_self
        )
        scores.append(round(score, 6))
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
        threshold_snapshot_hash=threshold_snapshot_hash,
        subsystem=subsystem,
    )
    return {"per_episode": per_episode, "aggregate_score": aggregate}


def obs_only_family_max(values: list[float]) -> float:
    return max(values) if values else 0.0


def run_obs_only_family(
    bundle: dict[str, Any],
    *,
    run_id: str,
    config: Config,
    threshold_snapshot_hash: str,
) -> dict[str, Any]:
    legal = [e["legal"] for e in bundle["episodes"]]
    family = obs_only_baseline(legal, run_id=f"{run_id}-obs-family", config=config)
    attackers = []
    value_level_values = []
    family_values = []
    for name, fn, value_level, weak in PASSIVE_ATTACKER_FAMILY:
        scored = _score_attacker(
            bundle=bundle,
            legal_episodes=legal,
            predictions=family["attackers"][name]["predictions"],
            producer_function=fn,
            run_id=f"{run_id}-{name}",
            config=config,
            subsystem="premise",
            threshold_snapshot_hash=threshold_snapshot_hash,
        )
        value = scored["aggregate_score"]["value"]
        family_values.append(value)
        if value_level:
            value_level_values.append(value)
        attackers.append(
            {
                "attacker": name,
                "value_level": value_level,
                "weak_diagnostic": weak,
                "aggregate_score": scored["aggregate_score"],
                "per_episode": scored["per_episode"],
            }
        )
    max_value = obs_only_family_max(family_values)
    max_attacker = max(attackers, key=lambda a: (a["aggregate_score"]["value"], a["attacker"]))["attacker"]
    value_level_max = obs_only_family_max(value_level_values)
    family_max_record = provenance.material_record(
        value=max_value,
        producer_function=obs_only_family_max,
        inputs={
            "attacker_values": {a["attacker"]: a["aggregate_score"]["value"] for a in attackers},
            "config_hash": provenance.sha256_json(bundle["config"]),
        },
        run_id=f"{run_id}-family-max",
        seed="multi_seed",
        episode_ids=[e["episode_id"] for e in bundle["episodes"]],
        aggregation="max_over_attacker_family",
        threshold_used=config.premise_threshold,
        threshold_snapshot_hash=threshold_snapshot_hash,
        subsystem="premise",
        recompute_basis={"kind": "max", "values": family_values},
    )
    return {
        "producer_function": provenance.producer_name(run_obs_only_family),
        "run_id": run_id,
        "attackers": attackers,
        "family_max": family_max_record,
        "family_max_attacker": max_attacker,
        "value_level_family_max": round(value_level_max, 6),
        "obs_only_family_max_score": max_value,
    }


def run_baseline_panel(
    bundle: dict[str, Any],
    *,
    run_id: str,
    threshold_snapshot_hash: str | None = None,
) -> dict[str, Any]:
    config = Config(**bundle["config"])
    if threshold_snapshot_hash is None:
        threshold_snapshot_hash = provenance.build_threshold_snapshot(config=config, config_type=Config)["snapshot_hash"]
    legal = [e["legal"] for e in bundle["episodes"]]
    obs = run_obs_only_family(
        bundle, run_id=f"{run_id}-obs-only", config=config, threshold_snapshot_hash=threshold_snapshot_hash
    )
    schema = _score_attacker(
        bundle=bundle,
        legal_episodes=legal,
        predictions=[
            {"episode_id": le["episode_id"], "predicted_self_handles": pred}
            for le, pred in zip(legal, schema_only_attacker(legal, config=config))
        ],
        producer_function=schema_only_attacker,
        run_id=f"{run_id}-schema",
        config=config,
        subsystem="schema_alias",
        threshold_snapshot_hash=threshold_snapshot_hash,
    )
    name = _score_attacker(
        bundle=bundle,
        legal_episodes=legal,
        predictions=[
            {"episode_id": le["episode_id"], "predicted_self_handles": pred}
            for le, pred in zip(legal, name_order_attacker(legal, config=config))
        ],
        producer_function=name_order_attacker,
        run_id=f"{run_id}-name-order",
        config=config,
        subsystem="schema_alias",
        threshold_snapshot_hash=threshold_snapshot_hash,
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
    obs = panel["obs_only"]["family_max"]["value"]
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
    }


# --------------------------------------------------------------------------- #
# Interventional oracle (ceiling only) + headroom gate
# --------------------------------------------------------------------------- #
def _predict_oracle_for_legal(legal: dict[str, Any]) -> list[str]:
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
    return sorted(ranked[: legal["query"]["k_self"]])


def run_interventional_oracle(
    bundle: dict[str, Any],
    *,
    run_id: str,
    threshold_snapshot_hash: str | None = None,
) -> dict[str, Any]:
    config = Config(**bundle["config"])
    if threshold_snapshot_hash is None:
        threshold_snapshot_hash = provenance.build_threshold_snapshot(config=config, config_type=Config)["snapshot_hash"]
    per_episode = []
    scores = []
    predictions = []
    legal_rows = []
    serialized_state = {"episodes": {}}
    for episode in bundle["episodes"]:
        legal = episode["interventional_legal"]
        predicted = _predict_oracle_for_legal(legal)
        score = score_self_set_prediction(predicted, episode["truth_self_handles"], k_self=config.k_self)
        scores.append(round(score, 6))
        per_episode.append({"episode_id": episode["episode_id"], "predicted_self_handles": predicted, "score": round(score, 6)})
        prediction_hash = provenance.sha256_json({"episode_id": episode["episode_id"], "predicted_self_handles": predicted})
        predictions.append(
            {"episode_id": episode["episode_id"], "predicted_self_handles": predicted, "prediction_hash": prediction_hash}
        )
        # Serialized state carries ONLY what replay legally needs to recompute.
        # No effect map / no answer is stored, so replay cannot shortcut.
        serialized_state["episodes"][episode["episode_id"]] = {
            "handles": legal["handles"],
            "k_self": legal["query"]["k_self"],
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
        threshold_snapshot_hash=threshold_snapshot_hash,
        subsystem="interventional_headroom",
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
    obs_attackers = {a["attacker"]: {row["episode_id"]: row for row in a["per_episode"]} for a in panel["obs_only"]["attackers"]}
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
                "obs_only_family": {name: by_ep[episode_id] for name, by_ep in obs_attackers.items()},
                "obs_only_family_max": panel["obs_only"]["family_max"]["value"],
                "obs_only_family_max_attacker": panel["obs_only"]["family_max_attacker"],
                "schema_only": schema_by_episode[episode_id],
                "name_order": name_by_episode[episode_id],
                "interventional_oracle": oracle_by_episode[episode_id],
                "claim_ceiling": CLAIM_CEILING,
            }
        )
    return rows
