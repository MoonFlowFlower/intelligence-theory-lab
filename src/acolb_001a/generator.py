import random

from .config import ACTION_BASIS, PROBE_ACTIONS, QUERY_ACTIONS
from .linear import dot
from .schemas import Episode, ProbeStep, Query


def _hidden_basis(action: str) -> tuple[float, float]:
    x0, x1 = ACTION_BASIS[action]
    return (1.0 * x0 + 0.18 * x1, -0.12 * x0 + 0.92 * x1)


def _episode_theta(seed: int, idx: int) -> tuple[float, float]:
    rng = random.Random(seed * 7919 + idx * 104729)
    return (rng.uniform(-1.25, 1.25), rng.uniform(-1.25, 1.25))


def _drift(regime: str, t: int) -> tuple[float, float]:
    if regime == "ood":
        return (0.16 * t, -0.11 * t)
    return (0.0, 0.0)


def _effective_theta(theta: tuple[float, float], regime: str, t: int) -> tuple[float, float]:
    d0, d1 = _drift(regime, t)
    return (theta[0] + d0, theta[1] + d1)


def _noise(seed: int, idx: int, t: int, action: str) -> float:
    rng = random.Random(seed * 37 + idx * 101 + t * 997 + sum(ord(ch) for ch in action))
    return rng.uniform(-0.015, 0.015)


def _outcome(theta: tuple[float, float], action: str, seed: int, idx: int, t: int) -> float:
    return dot(theta, _hidden_basis(action)) + _noise(seed, idx, t, action)


def generate_episode(regime: str, seed: int, idx: int) -> Episode:
    theta = _episode_theta(seed, idx)
    probes = []
    for t, action in enumerate(PROBE_ACTIONS):
        latent = _effective_theta(theta, regime, t)
        prediction_free_prior = 0.0
        observed = _outcome(latent, action, seed, idx, t)
        probes.append(
            ProbeStep(
                t=t,
                action=action,
                outcome=observed,
                latent_at_t=latent,
                pe_truth=observed - prediction_free_prior,
            )
        )
    final_t = len(PROBE_ACTIONS)
    final_theta = _effective_theta(theta, regime, final_t)
    queries = []
    for q_idx, action in enumerate(QUERY_ACTIONS):
        truth = _outcome(final_theta, action, seed, idx, final_t + q_idx)
        queries.append(
            Query(
                q_id=f"q{q_idx}",
                query_action=action,
                query_context={"query_index": q_idx},
                truth_outcome=truth,
                truth_producer="_outcome",
            )
        )
    return Episode(
        episode_id=f"{regime}-{seed}-{idx}",
        regime=regime,
        seed=seed,
        theta=theta,
        dynamics_params={"drift_x": _drift(regime, 1)[0], "drift_y": _drift(regime, 1)[1]},
        probes=tuple(probes),
        queries=tuple(queries),
        probe_action_set=tuple(PROBE_ACTIONS),
        query_action_set=tuple(QUERY_ACTIONS),
    )


def build_dataset(regime: str, seeds: list[int], episodes_per_seed: int = 1) -> list[Episode]:
    return [
        generate_episode(regime, seed, idx)
        for seed in seeds
        for idx in range(episodes_per_seed)
    ]
