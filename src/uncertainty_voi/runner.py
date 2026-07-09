"""Isolated runner for UNCERTAINTY-VOI-REQUEST-MECHANISM-001A.

This module implements only the frozen ITL toy-lab mechanism test.  It is not an
EGO runtime path and it does not expose any companion / UI / LLM integration.
"""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import inspect
import json
import math
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Sequence

import numpy as np


TASK_ID = "UNCERTAINTY-VOI-REQUEST-MECHANISM-001A"
EXPECTED_PREREG_SHA256 = "46031e0340f0e3eb3f65f22a1728eb925840dba9c890aa1aece375141b740180"
CLAIM_CEILING = (
    "Bounded VOI mechanism-proxy in one toy; not intelligence / adaptation / "
    "world-model / subject; not a claim about the pet. Strongest possible positive "
    "outcome = a bounded, replayable, attribution-checked VOI-mechanism-proxy result "
    "on this specific toy distribution."
)
VERDICT_SET = {
    "VOI_MECHANISM_PRESENT",
    "VOI_MECHANISM_PRESENT_UNCALIBRATED",
    "STATIC_SUFFICIENT",
    "ATTRIBUTION_FAILURE",
    "INSTRUMENT_INVALID",
    "CAPABILITY_ABSENT",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class FrozenConfig:
    task_id: str = TASK_ID
    k: int = 8
    horizon: int = 200
    tau_hi: float = 0.06
    tau_lo: float = 0.005
    sigma_obs: float = 0.10
    query_cost: float = 0.02
    request_cost: float = 0.08
    q: float = 0.004
    initial_mu: float = 0.5
    initial_var: float = 0.25
    request_kg_scale: float = 0.35
    scored_seeds: tuple[int, ...] = field(default_factory=lambda: tuple(range(9101, 9121)))
    transfer_seeds: tuple[int, ...] = field(default_factory=lambda: tuple(range(9201, 9211)))
    tuning_seeds: tuple[int, ...] = field(default_factory=lambda: tuple(range(9301, 9311)))
    probe_seed: int = 9001
    static_theta_grid: tuple[int, ...] = (0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144)
    static_request_period_grid: tuple[int, ...] = (0, 20, 40)
    bootstrap_reps: int = 4000
    bootstrap_seed: int = 20260709
    random_policy_seed_offset: int = 470_000
    shuffled_seed_offset: int = 820_000
    trace_size_cap_bytes: int = 25 * 1024 * 1024
    cpu_budget_seconds: float = 120.0
    fresh_process_recompute_count: int = 2
    prereg_path: Path = field(
        default_factory=lambda: _repo_root()
        / "artifacts"
        / TASK_ID
        / "preregistration.md"
    )
    artifact_dir: Path = field(default_factory=lambda: _repo_root() / "artifacts" / TASK_ID)


@dataclass
class RestlessGaussianBanditWorld:
    env_seed: int
    values: np.ndarray
    query_noise: np.ndarray
    request_noise: np.ndarray
    fast_arm_mask: np.ndarray
    slow_arm_mask: np.ndarray

    @classmethod
    def from_seed(cls, env_seed: int, cfg: FrozenConfig) -> "RestlessGaussianBanditWorld":
        rng = np.random.default_rng(int(env_seed))
        perm = rng.permutation(cfg.k)
        fast = np.zeros(cfg.k, dtype=bool)
        fast[perm[: cfg.k // 2]] = True
        slow = ~fast
        taus = np.where(fast, cfg.tau_hi, cfg.tau_lo)

        values = np.zeros((cfg.horizon + 1, cfg.k), dtype=float)
        values[0] = rng.uniform(0.0, 1.0, size=cfg.k)
        for t in range(cfg.horizon):
            values[t + 1] = np.clip(values[t] + rng.normal(0.0, taus, size=cfg.k), 0.0, 1.0)

        query_noise = rng.normal(0.0, cfg.sigma_obs, size=(cfg.horizon, cfg.k))
        request_noise = rng.normal(0.0, cfg.sigma_obs / 3.0, size=(cfg.horizon, cfg.k))
        return cls(
            env_seed=int(env_seed),
            values=values,
            query_noise=query_noise,
            request_noise=request_noise,
            fast_arm_mask=fast,
            slow_arm_mask=slow,
        )

    def observation_for(self, kind: str, t: int, arm: int) -> dict[str, Any]:
        if kind == "query":
            sigma = float(self.query_noise[t, arm] * 0.0 + FrozenConfig().sigma_obs)
            sample = float(self.values[t, arm] + self.query_noise[t, arm])
        elif kind == "request":
            sigma = float(FrozenConfig().sigma_obs / 3.0)
            sample = float(self.values[t, arm] + self.request_noise[t, arm])
        else:
            raise ValueError(f"unknown observation kind: {kind}")
        return {
            "sample": sample,
            "noise_sigma": sigma,
            "observation_kind": kind,
        }


@dataclass
class EpisodeResult:
    policy_id: str
    env_seed: int
    regret: float
    action_counts: dict[str, int]
    trace_rows: list[dict[str, Any]]
    calibration_sum_z2: float
    calibration_count: int
    calibration_coverage_count: int


def sha256_lf(data: bytes | str) -> str:
    raw = data.encode("utf-8") if isinstance(data, str) else data
    return hashlib.sha256(raw.replace(b"\r\n", b"\n")).hexdigest()


def source_file_sha256() -> str:
    return sha256_lf(Path(__file__).read_bytes())


def code_path_hash(func: Any) -> str:
    try:
        source = inspect.getsource(func)
    except (OSError, TypeError):
        source = repr(func)
    return sha256_lf(source)


def _normal_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2.0 * math.pi)


def _normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _round_float(value: float, ndigits: int = 17) -> float:
    if math.isfinite(float(value)):
        # Keep enough precision for JSON round-trip replay to recompute the same
        # post-state from serialized_state + observation.  Shorter presentation
        # rounding breaks the evidence contract by making replay fail for a
        # formatting reason rather than a behavior reason.
        return round(float(value), ndigits)
    return float(value)


def _round_list(values: Sequence[float]) -> list[float]:
    return [_round_float(float(v)) for v in values]


def _state_payload(mu: np.ndarray, var: np.ndarray) -> dict[str, Any]:
    return {
        "encoding": "float.hex",
        "mu": [float(x).hex() for x in mu.tolist()],
        "var": [float(x).hex() for x in var.tolist()],
    }


def _state_arrays(payload: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    if payload.get("encoding") == "float.hex":
        return (
            np.asarray([float.fromhex(str(x)) for x in payload["mu"]], dtype=float),
            np.asarray([float.fromhex(str(x)) for x in payload["var"]], dtype=float),
        )
    return np.asarray(payload["mu"], dtype=float), np.asarray(payload["var"], dtype=float)


def assert_seed_blocks_disjoint(cfg: FrozenConfig) -> bool:
    blocks = [
        {cfg.probe_seed},
        set(cfg.tuning_seeds),
        set(cfg.scored_seeds),
        set(cfg.transfer_seeds),
    ]
    for i, left in enumerate(blocks):
        for right in blocks[i + 1 :]:
            if left & right:
                raise ValueError(f"seed blocks overlap: {sorted(left & right)}")
    return True


def _initial_belief(cfg: FrozenConfig) -> tuple[np.ndarray, np.ndarray]:
    return (
        np.full(cfg.k, cfg.initial_mu, dtype=float),
        np.full(cfg.k, cfg.initial_var, dtype=float),
    )


def _inflate_variance(var: np.ndarray, cfg: FrozenConfig, *, uncertainty_ablation: bool) -> np.ndarray:
    if uncertainty_ablation:
        return np.full_like(var, cfg.initial_var)
    return var + cfg.q


def _kalman_update(
    mu: np.ndarray,
    var: np.ndarray,
    arm: int,
    sample: float,
    noise_sigma: float,
    cfg: FrozenConfig,
    *,
    uncertainty_ablation: bool,
) -> float:
    before = float(mu[arm])
    pe = abs(before - float(sample))
    gain = float(var[arm] / (var[arm] + noise_sigma * noise_sigma))
    mu[arm] = mu[arm] + gain * (float(sample) - mu[arm])
    var[arm] = var[arm] * (1.0 - gain)
    if uncertainty_ablation:
        var[arm] = cfg.initial_var
    return pe


def _query_kg_values(mu: np.ndarray, var: np.ndarray, cfg: FrozenConfig, *, value_ablation: bool) -> np.ndarray:
    sigma = np.sqrt(np.maximum(var, 1e-12))
    if value_ablation:
        return sigma.copy()
    out = np.zeros(cfg.k, dtype=float)
    for i in range(cfg.k):
        others = np.delete(mu, i)
        incumbent = float(np.max(others))
        z = float((mu[i] - incumbent) / max(sigma[i], 1e-9))
        out[i] = float(sigma[i] * (_normal_pdf(z) + z * _normal_cdf(z)))
    return out


def choose_mechanism_action(
    mu: np.ndarray,
    var: np.ndarray,
    cfg: FrozenConfig,
    *,
    value_ablation: bool = False,
) -> dict[str, Any]:
    query_kg = _query_kg_values(mu, var, cfg, value_ablation=value_ablation)
    query_scores = query_kg - cfg.query_cost
    top2 = np.argsort(mu)[-2:]
    request_kg = cfg.request_kg_scale * float(np.sum(np.sqrt(np.maximum(var[top2], 1e-12))) * (1.0 - 1.0 / 3.0))
    request_score = request_kg - cfg.request_cost
    best_query_arm = int(np.argmax(query_scores))
    best_query_score = float(query_scores[best_query_arm])
    if request_score > best_query_score:
        best_score = request_score
        best_action = {"kind": "request", "arms": [int(a) for a in top2.tolist()]}
    else:
        best_score = best_query_score
        best_action = {"kind": "query", "arm": best_query_arm}
    if best_score <= 0.0:
        return {"kind": "exploit", "arm": int(np.argmax(mu))}
    return best_action


def _choose_static_action(
    mu: np.ndarray,
    ages: np.ndarray,
    t: int,
    params: dict[str, int],
) -> dict[str, Any]:
    period = int(params.get("request_period", 0))
    if period > 0 and t > 0 and t % period == 0:
        top2 = np.argsort(mu)[-2:]
        return {"kind": "request", "arms": [int(a) for a in top2.tolist()]}
    theta = int(params.get("theta", 0))
    arm = int(np.argmax(ages))
    if int(ages[arm]) > theta:
        return {"kind": "query", "arm": arm}
    return {"kind": "exploit", "arm": int(np.argmax(mu))}


def _shuffled_sample_pool(world: RestlessGaussianBanditWorld, cfg: FrozenConfig) -> list[float]:
    pool = (world.values[: cfg.horizon] + world.query_noise).reshape(-1).astype(float)
    rng = np.random.default_rng(world.env_seed + cfg.shuffled_seed_offset)
    order = rng.permutation(pool.shape[0])
    return [float(pool[i]) for i in order.tolist()]


def _action_key(action: dict[str, Any]) -> str:
    return str(action["kind"])


def _observe_samples(
    world: RestlessGaussianBanditWorld,
    cfg: FrozenConfig,
    t: int,
    action: dict[str, Any],
    shuffled_pool: list[float],
    shuffled_index: int,
) -> tuple[list[dict[str, Any]], int]:
    kind = str(action["kind"])
    observations: list[dict[str, Any]] = []
    if kind == "query":
        arms = [int(action["arm"])]
        obs_kind = "query"
    elif kind == "request":
        arms = [int(a) for a in action["arms"]]
        obs_kind = "request"
    else:
        return observations, shuffled_index
    for arm in arms:
        if shuffled_pool:
            sample = shuffled_pool[shuffled_index % len(shuffled_pool)]
            shuffled_index += 1
            noise_sigma = cfg.sigma_obs
            source = "shuffled_pool"
        else:
            obs = world.observation_for(obs_kind, t, arm)
            sample = float(obs["sample"])
            noise_sigma = float(obs["noise_sigma"])
            source = obs_kind
        observations.append(
            {
                "arm": int(arm),
                "sample": float(sample),
                "noise_sigma": float(noise_sigma),
                "observation_kind": source,
            }
        )
    return observations, shuffled_index


def simulate_policy(
    policy_id: str,
    env_seed: int,
    cfg: FrozenConfig | None = None,
    *,
    static_params: dict[str, int] | None = None,
    trace: bool = False,
) -> EpisodeResult:
    cfg = cfg or FrozenConfig()
    world = RestlessGaussianBanditWorld.from_seed(int(env_seed), cfg)
    mu, var = _initial_belief(cfg)
    ages = np.full(cfg.k, cfg.horizon, dtype=int)
    regret = 0.0
    action_counts = {"query": 0, "request": 0, "exploit": 0, "oracle": 0}
    trace_rows: list[dict[str, Any]] = []
    calibration_sum_z2 = 0.0
    calibration_count = 0
    calibration_coverage_count = 0
    shuffled_pool = _shuffled_sample_pool(world, cfg) if policy_id == "shuffled" else []
    shuffled_index = 0
    rng = np.random.default_rng(int(env_seed) + cfg.random_policy_seed_offset)

    uncertainty_ablation = policy_id == "uncertainty_ablation"
    value_ablation = policy_id == "value_ablation"
    no_update = policy_id == "no_update"

    if policy_id == "static_threshold" and not static_params:
        raise ValueError("static_threshold requires static_params")

    for t in range(cfg.horizon):
        var = _inflate_variance(var, cfg, uncertainty_ablation=uncertainty_ablation)

        if policy_id in {"mechanism", "wrong_sign", "shuffled", "uncertainty_ablation", "value_ablation", "no_update"}:
            action = choose_mechanism_action(mu, var, cfg, value_ablation=value_ablation)
        elif policy_id == "static_threshold":
            action = _choose_static_action(mu, ages, t, static_params or {})
        elif policy_id == "random_query":
            action = {"kind": "query", "arm": int(rng.integers(0, cfg.k))}
        elif policy_id == "exploit_only":
            action = {"kind": "exploit", "arm": int(np.argmax(mu))}
        elif policy_id == "oracle":
            action = {"kind": "oracle", "arm": int(np.argmax(world.values[t]))}
        else:
            raise ValueError(f"unknown policy_id: {policy_id}")

        if policy_id == "mechanism":
            sigma = np.sqrt(np.maximum(var, 1e-12))
            z = (mu - world.values[t]) / sigma
            calibration_sum_z2 += float(np.sum(z * z))
            calibration_count += cfg.k
            calibration_coverage_count += int(np.sum(np.abs(z) <= 1.645))

        pre_mu = mu.copy()
        pre_var = var.copy()
        action_kind = _action_key(action)
        if action_kind in action_counts:
            action_counts[action_kind] += 1
        else:
            action_counts[action_kind] = 1

        max_value = float(np.max(world.values[t]))
        if action_kind in {"exploit", "oracle"}:
            chosen = int(action["arm"])
            if action_kind == "oracle":
                regret_t = 0.0
            else:
                regret_t = max_value - float(world.values[t, chosen])
            observations: list[dict[str, Any]] = []
        else:
            cost = cfg.query_cost if action_kind == "query" else cfg.request_cost
            regret_t = max_value + cost
            observations, shuffled_index = _observe_samples(world, cfg, t, action, shuffled_pool, shuffled_index)
            ages += 1
            for obs in observations:
                arm = int(obs["arm"])
                ages[arm] = 0
                update_sample = float(obs["sample"])
                if policy_id == "wrong_sign":
                    update_sample = float(2.0 * mu[arm] - update_sample)
                if not no_update:
                    pe = _kalman_update(
                        mu,
                        var,
                        arm,
                        update_sample,
                        float(obs["noise_sigma"]),
                        cfg,
                        uncertainty_ablation=uncertainty_ablation,
                    )
                else:
                    pe = abs(float(mu[arm]) - update_sample)
                obs["update_sample"] = float(update_sample)
                obs["prediction_error"] = float(pe)
        if action_kind in {"exploit", "oracle"}:
            ages += 1

        regret += regret_t
        if trace:
            trace_rows.append(
                {
                    "task_id": TASK_ID,
                    "env_seed": int(env_seed),
                    "t": int(t),
                    "policy_id": policy_id,
                    "serialized_state": _state_payload(pre_mu, pre_var),
                    "action": copy.deepcopy(action),
                    "observation": copy.deepcopy(observations),
                    "post_state": _state_payload(mu, var),
                    "regret": _round_float(regret_t),
                }
            )

    return EpisodeResult(
        policy_id=policy_id,
        env_seed=int(env_seed),
        regret=float(regret),
        action_counts=action_counts,
        trace_rows=trace_rows,
        calibration_sum_z2=float(calibration_sum_z2),
        calibration_count=int(calibration_count),
        calibration_coverage_count=int(calibration_coverage_count),
    )


def tune_static_threshold(cfg: FrozenConfig | None = None) -> dict[str, Any]:
    cfg = cfg or FrozenConfig()
    rows: list[dict[str, Any]] = []
    best: dict[str, Any] | None = None
    for theta in cfg.static_theta_grid:
        for period in cfg.static_request_period_grid:
            params = {"theta": int(theta), "request_period": int(period)}
            regrets = [
                simulate_policy("static_threshold", seed, cfg, static_params=params).regret
                for seed in cfg.tuning_seeds
            ]
            row = {
                "params": params,
                "mean_regret": float(np.mean(regrets)),
                "regrets": [float(x) for x in regrets],
            }
            rows.append(row)
            if best is None or (row["mean_regret"], theta, period) < (
                best["mean_regret"],
                best["params"]["theta"],
                best["params"]["request_period"],
            ):
                best = row
    assert best is not None
    return {
        "producer_function": "uncertainty_voi.runner.tune_static_threshold",
        "code_path_hash": code_path_hash(tune_static_threshold),
        "used_seeds": [int(s) for s in cfg.tuning_seeds],
        "grid_results": rows,
        "best_params": best["params"],
        "best_mean_regret": best["mean_regret"],
        "aggregation_rule": "minimize mean cumulative regret over frozen tuning seeds; ties by theta then request_period",
    }


def _paired_stats(values: Sequence[float], cfg: FrozenConfig, *, label: str) -> dict[str, Any]:
    arr = np.asarray(values, dtype=float)
    n = int(arr.shape[0])
    if n == 0:
        raise ValueError("empty paired stats input")
    rng = np.random.default_rng(cfg.bootstrap_seed + int(sha256_lf(label)[:8], 16) % 1_000_000)
    means = np.empty(cfg.bootstrap_reps, dtype=float)
    for i in range(cfg.bootstrap_reps):
        idx = rng.integers(0, n, size=n)
        means[i] = float(np.mean(arr[idx]))
    low, high = np.quantile(means, [0.025, 0.975])
    std = float(np.std(arr, ddof=1)) if n > 1 else 0.0
    return {
        "n": n,
        "mean": float(np.mean(arr)),
        "ci95": [float(low), float(high)],
        "std": std,
        "effect_size_mean_over_sd": float(np.mean(arr) / std) if std > 0.0 else None,
        "values": [float(x) for x in arr.tolist()],
        "aggregation_rule": f"paired bootstrap mean CI with {cfg.bootstrap_reps} resamples",
    }


def _ci_excludes_zero_positive(stats: dict[str, Any]) -> bool:
    return float(stats["ci95"][0]) > 0.0 and float(stats["mean"]) > 0.0


def _ci_includes_zero(stats: dict[str, Any]) -> bool:
    low, high = stats["ci95"]
    return float(low) <= 0.0 <= float(high)


def _condition_results(
    condition_policy_id: str,
    seeds: Sequence[int],
    cfg: FrozenConfig,
    static_params: dict[str, int],
    *,
    trace_mechanism: bool = False,
) -> dict[str, Any]:
    mech_results = [
        simulate_policy(condition_policy_id, seed, cfg, trace=trace_mechanism)
        for seed in seeds
    ]
    static_results = [
        simulate_policy("static_threshold", seed, cfg, static_params=static_params)
        for seed in seeds
    ]
    advantages = [s.regret - m.regret for m, s in zip(mech_results, static_results)]
    return {
        "policy_id": condition_policy_id,
        "seeds": [int(s) for s in seeds],
        "mechanism_regrets": [float(r.regret) for r in mech_results],
        "static_regrets": [float(r.regret) for r in static_results],
        "advantages": [float(a) for a in advantages],
        "advantage_stats": _paired_stats(advantages, cfg, label=f"{condition_policy_id}:{list(seeds)}"),
        "mechanism_action_counts": _sum_action_counts(mech_results),
        "static_action_counts": _sum_action_counts(static_results),
        "trace_rows": [row for r in mech_results for row in r.trace_rows],
        "calibration": _aggregate_calibration(mech_results),
    }


def _sum_action_counts(results: Sequence[EpisodeResult]) -> dict[str, int]:
    out: dict[str, int] = {}
    for result in results:
        for key, value in result.action_counts.items():
            out[key] = out.get(key, 0) + int(value)
    return out


def _aggregate_calibration(results: Sequence[EpisodeResult]) -> dict[str, Any]:
    total = sum(r.calibration_count for r in results)
    if total <= 0:
        return {"mean_z2": None, "coverage90_fraction": None, "count": 0}
    return {
        "mean_z2": float(sum(r.calibration_sum_z2 for r in results) / total),
        "coverage90_fraction": float(sum(r.calibration_coverage_count for r in results) / total),
        "count": int(total),
    }


def _floor_results(seeds: Sequence[int], cfg: FrozenConfig) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for policy_id in ("random_query", "exploit_only", "no_update", "oracle"):
        results = [simulate_policy(policy_id, seed, cfg) for seed in seeds]
        out[policy_id] = {
            "seeds": [int(s) for s in seeds],
            "regrets": [float(r.regret) for r in results],
            "mean_regret": float(np.mean([r.regret for r in results])),
            "action_counts": _sum_action_counts(results),
        }
    return out


def replay_trace(trace_rows: Sequence[dict[str, Any]], cfg: FrozenConfig | None = None) -> dict[str, Any]:
    cfg = cfg or FrozenConfig()
    mismatches: list[str] = []
    for row in trace_rows:
        mu, var = _state_arrays(row["serialized_state"])
        policy_id = str(row["policy_id"])
        expected_action = choose_mechanism_action(
            mu,
            var,
            cfg,
            value_ablation=(policy_id == "value_ablation"),
        )
        if expected_action != row["action"]:
            mismatches.append(f"action_mismatch seed={row['env_seed']} t={row['t']}")
            continue
        for obs in row["observation"]:
            arm = int(obs["arm"])
            _kalman_update(
                mu,
                var,
                arm,
                float(obs["update_sample"]),
                float(obs["noise_sigma"]),
                cfg,
                uncertainty_ablation=(policy_id == "uncertainty_ablation"),
            )
        post_payload = _state_payload(mu, var)
        if post_payload != row["post_state"]:
            mismatches.append(f"state_mismatch seed={row['env_seed']} t={row['t']}")
    return {
        "producer_function": "uncertainty_voi.runner.replay_trace",
        "code_path_hash": code_path_hash(replay_trace),
        "bit_exact": not mismatches,
        "passed": not mismatches,
        "mismatches": mismatches[:20],
        "checked_rows": int(len(trace_rows)),
        "uses_hash_only_comparison": False,
        "uses_stored_outputs_only": False,
        "recomputed_from_serialized_state_and_observation": True,
    }


def _tamper_replay_control(trace_rows: Sequence[dict[str, Any]], cfg: FrozenConfig) -> dict[str, Any]:
    if not trace_rows:
        return {"detected": False, "reason": "no_trace_rows"}
    tampered = [copy.deepcopy(row) for row in trace_rows]
    tampered[0]["action"] = {"kind": "exploit", "arm": 0}
    report = replay_trace(tampered, cfg)
    return {
        "detected": not report["bit_exact"],
        "mismatch_sample": report["mismatches"][:3],
    }


class _RngAuditVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.violations: list[str] = []

    def visit_Call(self, node: ast.Call) -> Any:
        name = _call_name(node.func)
        if name in {"np.random.random", "np.random.normal", "numpy.random.random", "numpy.random.normal"}:
            self.violations.append(f"unseeded_global_rng:{name}:line{node.lineno}")
        if name in {"np.random.default_rng", "numpy.random.default_rng"} and len(node.args) == 0 and not node.keywords:
            self.violations.append(f"default_rng_without_seed:{name}:line{node.lineno}")
        if name in {"random.random", "random.gauss", "random.randrange"}:
            self.violations.append(f"python_random_global:{name}:line{node.lineno}")
        self.generic_visit(node)


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def scan_rng_source(source: str) -> dict[str, Any]:
    visitor = _RngAuditVisitor()
    visitor.visit(ast.parse(source))
    return {
        "passed": not visitor.violations,
        "violations": visitor.violations,
    }


def run_rng_audit() -> dict[str, Any]:
    source = Path(__file__).read_text(encoding="utf-8")
    positive_control = "import numpy as np\nx = np.random.default_rng().normal()\n"
    clean = scan_rng_source(source)
    pc = scan_rng_source(positive_control)
    return {
        "producer_function": "uncertainty_voi.runner.run_rng_audit",
        "code_path_hash": code_path_hash(run_rng_audit),
        "clean_scan": clean,
        "positive_control": {
            "source": positive_control,
            "detected": not pc["passed"],
            "violations": pc["violations"],
        },
        "passed": clean["passed"] and (not pc["passed"]),
        "aggregation_rule": "actual source must be clean and synthetic unseeded default_rng positive control must be detected",
    }


def _json_ready(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_ready(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(v) for v in value]
    if isinstance(value, np.ndarray):
        return _json_ready(value.tolist())
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    return value


def canonical_json_bytes(payload: Any) -> bytes:
    return json.dumps(_json_ready(payload), sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def _payload_digest(payload: Any) -> str:
    return hashlib.sha256(canonical_json_bytes(payload)).hexdigest()


def _build_metric_record(
    *,
    metric_id: str,
    producer_function: str,
    value: Any,
    input_artifacts: Sequence[str],
    seeds: Sequence[int],
    aggregation_rule: str,
    code_hash: str | None = None,
) -> dict[str, Any]:
    return {
        "metric_id": metric_id,
        "producer_function": producer_function,
        "input_artifacts": list(input_artifacts),
        "run_id": f"{TASK_ID}:R3:{sha256_lf(str(list(seeds)) + metric_id)[:12]}",
        "seed_ids": [int(s) for s in seeds],
        "aggregation_rule": aggregation_rule,
        "code_path_hash": code_hash or source_file_sha256(),
        "value": _json_ready(value),
    }


def _cost_projection(cfg: FrozenConfig, start_time: float, probe_elapsed: float) -> dict[str, Any]:
    evaluated_episode_count = (
        len(cfg.tuning_seeds) * len(cfg.static_theta_grid) * len(cfg.static_request_period_grid)
        + len(cfg.scored_seeds) * 9
        + len(cfg.transfer_seeds) * 2
        + 2
    )
    projected = max(probe_elapsed, 1e-6) * evaluated_episode_count / 2.0
    return {
        "producer_function": "uncertainty_voi.runner._cost_projection",
        "code_path_hash": code_path_hash(_cost_projection),
        "probe_elapsed_seconds": float(probe_elapsed),
        "projected_seconds": float(projected),
        "cpu_budget_seconds": float(cfg.cpu_budget_seconds),
        "evaluated_episode_count_projection": int(evaluated_episode_count),
        "within_budget": bool(projected <= cfg.cpu_budget_seconds),
        "started_at_monotonic": float(start_time),
    }


def _compute_core_payload(cfg: FrozenConfig) -> dict[str, Any]:
    assert_seed_blocks_disjoint(cfg)
    probe_start = time.perf_counter()
    probe_mechanism = simulate_policy("mechanism", cfg.probe_seed, cfg)
    probe_static_params = {"theta": int(cfg.static_theta_grid[0]), "request_period": int(cfg.static_request_period_grid[0])}
    probe_static = simulate_policy("static_threshold", cfg.probe_seed, cfg, static_params=probe_static_params)
    probe_elapsed = time.perf_counter() - probe_start
    projection = _cost_projection(cfg, probe_start, probe_elapsed)
    if not projection["within_budget"]:
        return {
            "stopped": True,
            "stop_reason": "CPU_PROJECTION_EXCEEDS_PRESET_BUDGET",
            "probe": {
                "seed": cfg.probe_seed,
                "mechanism_regret": probe_mechanism.regret,
                "static_regret_default": probe_static.regret,
            },
            "cost_projection": projection,
        }

    tuning = tune_static_threshold(cfg)
    static_params = tuning["best_params"]

    clean = _condition_results("mechanism", cfg.scored_seeds, cfg, static_params, trace_mechanism=True)
    wrong = _condition_results("wrong_sign", cfg.scored_seeds, cfg, static_params)
    shuffled = _condition_results("shuffled", cfg.scored_seeds, cfg, static_params)
    uncertainty = _condition_results("uncertainty_ablation", cfg.scored_seeds, cfg, static_params)
    value = _condition_results("value_ablation", cfg.scored_seeds, cfg, static_params)
    transfer = _condition_results("mechanism", cfg.transfer_seeds, cfg, static_params)
    floors = _floor_results(cfg.scored_seeds, cfg)
    rng_audit = run_rng_audit()

    clean_adv = np.asarray(clean["advantages"], dtype=float)
    wrong_adv = np.asarray(wrong["advantages"], dtype=float)
    shuffled_adv = np.asarray(shuffled["advantages"], dtype=float)
    uncertainty_adv = np.asarray(uncertainty["advantages"], dtype=float)
    value_adv = np.asarray(value["advantages"], dtype=float)
    wrong_collapse = _paired_stats((clean_adv - wrong_adv).tolist(), cfg, label="collapse:wrong")
    shuffled_collapse = _paired_stats((clean_adv - shuffled_adv).tolist(), cfg, label="collapse:shuffled")
    value_collapse = _paired_stats((clean_adv - value_adv).tolist(), cfg, label="collapse:value")

    mean_static = float(np.mean(clean["static_regrets"]))
    mean_mech = float(np.mean(clean["mechanism_regrets"]))
    mean_random = float(floors["random_query"]["mean_regret"])
    mean_exploit = float(floors["exploit_only"]["mean_regret"])
    mean_no_update = float(floors["no_update"]["mean_regret"])
    rel_advantage = float(clean["advantage_stats"]["mean"] / mean_static) if mean_static > 0 else 0.0
    calibration = clean["calibration"]

    gates = {
        "G1_rival_beat": {
            "passed": bool(_ci_excludes_zero_positive(clean["advantage_stats"]) and rel_advantage >= 0.10),
            "mean_relative_advantage": rel_advantage,
            "advantage_stats": clean["advantage_stats"],
        },
        "G2_falsifiers": {
            "passed": bool(
                _ci_includes_zero(wrong["advantage_stats"])
                and _ci_includes_zero(shuffled["advantage_stats"])
                and _ci_excludes_zero_positive(wrong_collapse)
                and _ci_excludes_zero_positive(shuffled_collapse)
            ),
            "wrong_sign_advantage_stats": wrong["advantage_stats"],
            "shuffled_advantage_stats": shuffled["advantage_stats"],
            "clean_minus_wrong_sign": wrong_collapse,
            "clean_minus_shuffled": shuffled_collapse,
        },
        "G3_ablations": {
            "passed": bool(_ci_includes_zero(uncertainty["advantage_stats"]) and _ci_excludes_zero_positive(value_collapse)),
            "uncertainty_ablation_advantage_stats": uncertainty["advantage_stats"],
            "value_ablation_advantage_stats": value["advantage_stats"],
            "clean_minus_value_ablation": value_collapse,
        },
        "G4a_calibration": {
            "passed": bool(calibration["mean_z2"] is not None and 0.7 <= float(calibration["mean_z2"]) <= 1.5),
            "mean_z2": calibration["mean_z2"],
            "coverage90_fraction": calibration["coverage90_fraction"],
            "tolerance": [0.7, 1.5],
        },
        "G4b_transfer": {
            "passed": bool(_ci_excludes_zero_positive(transfer["advantage_stats"])),
            "advantage_stats": transfer["advantage_stats"],
        },
        "G6_headroom": {
            "passed": bool(
                mean_random >= 2.0 * mean_mech
                and mean_exploit >= 2.0 * mean_mech
                and mean_static >= 0.10 * mean_random
            ),
            "floor_ratios": {
                "random_query_over_mechanism": float(mean_random / mean_mech) if mean_mech > 0 else None,
                "exploit_only_over_mechanism": float(mean_exploit / mean_mech) if mean_mech > 0 else None,
                "no_update_over_mechanism": float(mean_no_update / mean_mech) if mean_mech > 0 else None,
            },
            "static_headroom_fraction_of_random_to_oracle": float(mean_static / mean_random) if mean_random > 0 else None,
            "oracle_regret": 0.0,
        },
    }

    trace_rows = clean["trace_rows"]
    replay = replay_trace(trace_rows, cfg)
    tamper = _tamper_replay_control(trace_rows, cfg)
    trace_size_bytes = sum(len(json.dumps(row, sort_keys=True, separators=(",", ":"))) + 1 for row in trace_rows)
    gates["G5_replay_rng_trace"] = {
        "passed": bool(replay["bit_exact"] and tamper["detected"] and rng_audit["passed"] and trace_size_bytes <= cfg.trace_size_cap_bytes),
        "replay_bit_exact": replay["bit_exact"],
        "tamper_negative_control_detected": tamper["detected"],
        "rng_audit_passed": rng_audit["passed"],
        "trace_size_bytes": int(trace_size_bytes),
        "trace_size_cap_bytes": int(cfg.trace_size_cap_bytes),
    }

    verdict, subtype, positive_claim = _derive_verdict(gates, mean_mech, mean_random, mean_exploit)
    return {
        "stopped": False,
        "probe": {
            "seed": cfg.probe_seed,
            "mechanism_regret": probe_mechanism.regret,
            "static_regret_default": probe_static.regret,
        },
        "cost_projection": projection,
        "tuning": tuning,
        "clean": _drop_trace(clean),
        "wrong_sign": _drop_trace(wrong),
        "shuffled": _drop_trace(shuffled),
        "uncertainty_ablation": _drop_trace(uncertainty),
        "value_ablation": _drop_trace(value),
        "transfer": _drop_trace(transfer),
        "floors": floors,
        "gates": gates,
        "replay_report": {**replay, "tamper_negative_control": tamper},
        "rng_audit": rng_audit,
        "trace_rows": trace_rows,
        "trace_size_bytes": int(trace_size_bytes),
        "verdict": verdict,
        "verdict_subtype": subtype,
        "positive_claim": bool(positive_claim),
    }


def _drop_trace(payload: dict[str, Any]) -> dict[str, Any]:
    out = dict(payload)
    out.pop("trace_rows", None)
    return out


def _derive_verdict(
    gates: dict[str, Any],
    mean_mech: float,
    mean_random: float,
    mean_exploit: float,
) -> tuple[str, str, bool]:
    g1 = bool(gates["G1_rival_beat"]["passed"])
    g2 = bool(gates["G2_falsifiers"]["passed"])
    g3 = bool(gates["G3_ablations"]["passed"])
    g4a = bool(gates["G4a_calibration"]["passed"])
    g4b = bool(gates["G4b_transfer"]["passed"])
    g5 = bool(gates["G5_replay_rng_trace"]["passed"])
    g6 = bool(gates["G6_headroom"]["passed"])
    if not g5:
        return "INSTRUMENT_INVALID", "G5_REPLAY_RNG_TRACE_FAILED", False
    if not g6:
        return "INSTRUMENT_INVALID", "G6_HEADROOM_FAILED", False
    if mean_mech >= min(mean_random, mean_exploit):
        return "CAPABILITY_ABSENT", "MECHANISM_NOT_BETTER_THAN_FLOORS", False
    if g1 and g2 and g3 and g4a and g4b and g5 and g6:
        return "VOI_MECHANISM_PRESENT", "ALL_GATES_PASS", True
    if g1 and g2 and g3 and (not g4a) and g4b and g5 and g6:
        return "VOI_MECHANISM_PRESENT_UNCALIBRATED", "G4A_CALIBRATION_FAILED", True
    if not g1:
        return "STATIC_SUFFICIENT", "G1_RIVAL_BEAT_FAILED", False
    if not g2 or not g3:
        return "ATTRIBUTION_FAILURE", "FALSIFIER_OR_ABLATION_SURVIVED", False
    return "INSTRUMENT_INVALID", "UNCLASSIFIED_GATE_FAILURE", False


def _fresh_process_recompute(cfg: FrozenConfig, expected_digest: str) -> dict[str, Any]:
    if cfg.fresh_process_recompute_count <= 0:
        return {
            "fresh_process_recompute_count": 0,
            "bit_exact": True,
            "digests": [],
            "skipped": True,
        }
    digests: list[str] = []
    outputs: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory() as tmp:
        for i in range(cfg.fresh_process_recompute_count):
            out = Path(tmp) / f"recompute_{i}.json"
            env = os.environ.copy()
            src_path = str(_repo_root() / "src")
            env["PYTHONPATH"] = src_path + os.pathsep + env.get("PYTHONPATH", "")
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "uncertainty_voi.runner",
                    "--mode",
                    "recompute",
                    "--json-output",
                    str(out),
                ],
                cwd=_repo_root(),
                env=env,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            payload = json.loads(out.read_text(encoding="utf-8"))
            digests.append(str(payload["core_digest"]))
            outputs.append(payload)
    return {
        "producer_function": "uncertainty_voi.runner._fresh_process_recompute",
        "code_path_hash": code_path_hash(_fresh_process_recompute),
        "fresh_process_recompute_count": int(cfg.fresh_process_recompute_count),
        "expected_digest": expected_digest,
        "digests": digests,
        "bit_exact": all(d == expected_digest for d in digests),
        "outputs": outputs,
    }


def _core_for_digest(core: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in core.items()
        if key
        not in {
            "trace_rows",
            "replay_report",
            "rng_audit",
            "cost_projection",
        }
    }


def _build_artifacts_payload(cfg: FrozenConfig, core: dict[str, Any], replay_report: dict[str, Any]) -> dict[str, Any]:
    prereg_sha = sha256_lf(cfg.prereg_path.read_bytes())
    code_hash = source_file_sha256()
    config_shas = {
        "preregistration_lf_sha256": prereg_sha,
        "runner_source_lf_sha256": code_hash,
    }
    records = _metric_records(cfg, core, replay_report, config_shas)
    result = {
        "task_id": TASK_ID,
        "producer_function": "uncertainty_voi.runner.run_gate",
        "code_path_hash": code_path_hash(run_gate),
        "verdict": core["verdict"],
        "verdict_subtype": core["verdict_subtype"],
        "positive_claim": bool(core["positive_claim"]),
        "claim_ceiling": CLAIM_CEILING,
        "config_shas": config_shas,
        "run_id": f"{TASK_ID}:R3:{_payload_digest(_core_for_digest(core))[:12]}",
        "seed_blocks": {
            "probe": [cfg.probe_seed],
            "tuning": list(cfg.tuning_seeds),
            "scored": list(cfg.scored_seeds),
            "transfer": list(cfg.transfer_seeds),
        },
        "static_threshold_params": core["tuning"]["best_params"],
        "gates": core["gates"],
        "advantage_tables": {
            "clean": core["clean"]["advantage_stats"],
            "wrong_sign": core["wrong_sign"]["advantage_stats"],
            "shuffled": core["shuffled"]["advantage_stats"],
            "uncertainty_ablation": core["uncertainty_ablation"]["advantage_stats"],
            "value_ablation": core["value_ablation"]["advantage_stats"],
            "transfer": core["transfer"]["advantage_stats"],
        },
        "cost_projection": core["cost_projection"],
    }
    baseline_comparison = {
        "task_id": TASK_ID,
        "producer_function": "uncertainty_voi.runner._build_artifacts_payload/baseline_comparison",
        "code_path_hash": code_hash,
        "static_threshold_tuning": core["tuning"],
        "clean_scored": core["clean"],
        "floors": core["floors"],
        "oracle": core["floors"]["oracle"],
        "claim_ceiling": CLAIM_CEILING,
    }
    ablation_report = {
        "task_id": TASK_ID,
        "producer_function": "uncertainty_voi.runner._build_artifacts_payload/ablation_report",
        "code_path_hash": code_hash,
        "uncertainty_ablation": core["uncertainty_ablation"],
        "value_ablation": core["value_ablation"],
        "gate": core["gates"]["G3_ablations"],
        "claim_ceiling": CLAIM_CEILING,
    }
    falsifier_report = {
        "task_id": TASK_ID,
        "producer_function": "uncertainty_voi.runner._build_artifacts_payload/falsifier_report",
        "code_path_hash": code_hash,
        "wrong_sign": core["wrong_sign"],
        "shuffled": core["shuffled"],
        "gate": core["gates"]["G2_falsifiers"],
        "claim_ceiling": CLAIM_CEILING,
    }
    calibration_transfer_report = {
        "task_id": TASK_ID,
        "producer_function": "uncertainty_voi.runner._build_artifacts_payload/calibration_transfer_report",
        "code_path_hash": code_hash,
        "G4a": core["gates"]["G4a_calibration"],
        "G4b": core["gates"]["G4b_transfer"],
        "transfer": core["transfer"],
        "claim_ceiling": CLAIM_CEILING,
    }
    headroom_report = {
        "task_id": TASK_ID,
        "producer_function": "uncertainty_voi.runner._build_artifacts_payload/headroom_report",
        "code_path_hash": code_hash,
        "G6": core["gates"]["G6_headroom"],
        "floors": core["floors"],
        "static_mean_regret": float(np.mean(core["clean"]["static_regrets"])),
        "mechanism_mean_regret": float(np.mean(core["clean"]["mechanism_regrets"])),
        "oracle_regret": 0.0,
        "claim_ceiling": CLAIM_CEILING,
    }
    metric_records = {
        "task_id": TASK_ID,
        "producer_function": "uncertainty_voi.runner._metric_records",
        "code_path_hash": code_path_hash(_metric_records),
        "records": records,
    }
    failure_manifest = _failure_manifest(core, replay_report)
    return {
        "result.json": result,
        "baseline_comparison.json": baseline_comparison,
        "ablation_report.json": ablation_report,
        "falsifier_report.json": falsifier_report,
        "calibration_transfer_report.json": calibration_transfer_report,
        "headroom_report.json": headroom_report,
        "replay_report.json": replay_report,
        "metric_records.json": metric_records,
        "failure_manifest.json": failure_manifest,
    }


def _metric_records(
    cfg: FrozenConfig,
    core: dict[str, Any],
    replay_report: dict[str, Any],
    config_shas: dict[str, str],
) -> list[dict[str, Any]]:
    records = [
        _build_metric_record(
            metric_id="clean_advantage",
            producer_function="uncertainty_voi.runner._condition_results",
            value=core["clean"]["advantage_stats"],
            input_artifacts=["preregistration.md"],
            seeds=cfg.scored_seeds,
            aggregation_rule=core["clean"]["advantage_stats"]["aggregation_rule"],
            code_hash=code_path_hash(_condition_results),
        ),
        _build_metric_record(
            metric_id="static_threshold_tuning",
            producer_function="uncertainty_voi.runner.tune_static_threshold",
            value=core["tuning"]["best_params"],
            input_artifacts=["preregistration.md"],
            seeds=cfg.tuning_seeds,
            aggregation_rule=core["tuning"]["aggregation_rule"],
            code_hash=code_path_hash(tune_static_threshold),
        ),
        _build_metric_record(
            metric_id="G2_falsifiers",
            producer_function="uncertainty_voi.runner._derive_verdict",
            value=core["gates"]["G2_falsifiers"],
            input_artifacts=["falsifier_report.json"],
            seeds=cfg.scored_seeds,
            aggregation_rule="wrong_sign and shuffled collapse gates from paired callable reruns",
            code_hash=code_path_hash(_derive_verdict),
        ),
        _build_metric_record(
            metric_id="G3_ablations",
            producer_function="uncertainty_voi.runner._derive_verdict",
            value=core["gates"]["G3_ablations"],
            input_artifacts=["ablation_report.json"],
            seeds=cfg.scored_seeds,
            aggregation_rule="uncertainty and value ablations rerun under real interventions",
            code_hash=code_path_hash(_derive_verdict),
        ),
        _build_metric_record(
            metric_id="G4_calibration_transfer",
            producer_function="uncertainty_voi.runner._derive_verdict",
            value={"G4a": core["gates"]["G4a_calibration"], "G4b": core["gates"]["G4b_transfer"]},
            input_artifacts=["calibration_transfer_report.json"],
            seeds=tuple(cfg.scored_seeds) + tuple(cfg.transfer_seeds),
            aggregation_rule="offline calibration from hidden values for scoring only plus transfer paired CI",
            code_hash=code_path_hash(_derive_verdict),
        ),
        _build_metric_record(
            metric_id="G5_replay_rng_trace",
            producer_function="uncertainty_voi.runner.replay_trace",
            value=core["gates"]["G5_replay_rng_trace"],
            input_artifacts=["trace.jsonl", "replay_report.json"],
            seeds=cfg.scored_seeds,
            aggregation_rule="trace replay recomputes action/state and RNG audit positive control fires",
            code_hash=code_path_hash(replay_trace),
        ),
        _build_metric_record(
            metric_id="fresh_process_recompute",
            producer_function="uncertainty_voi.runner._fresh_process_recompute",
            value=replay_report.get("fresh_process_recompute", {}),
            input_artifacts=["result.json"],
            seeds=tuple(cfg.scored_seeds) + tuple(cfg.transfer_seeds) + tuple(cfg.tuning_seeds),
            aggregation_rule="two fresh-process core recomputes must match canonical core digest",
            code_hash=code_path_hash(_fresh_process_recompute),
        ),
        _build_metric_record(
            metric_id="config_shas",
            producer_function="uncertainty_voi.runner.sha256_lf",
            value=config_shas,
            input_artifacts=["preregistration.md", "runner.py"],
            seeds=[],
            aggregation_rule="LF-normalized SHA-256 readback",
            code_hash=code_path_hash(sha256_lf),
        ),
    ]
    return records


def _failure_manifest(core: dict[str, Any], replay_report: dict[str, Any]) -> dict[str, Any]:
    failures: list[dict[str, Any]] = []
    for gate_id, gate in core["gates"].items():
        if not gate.get("passed", False):
            failures.append({"gate": gate_id, "status": "failed", "details": gate})
    if core["verdict"] not in {"VOI_MECHANISM_PRESENT", "VOI_MECHANISM_PRESENT_UNCALIBRATED"}:
        failures.append(
            {
                "verdict": core["verdict"],
                "subtype": core["verdict_subtype"],
                "status": "non_positive_or_invalid_boundary",
            }
        )
    if not replay_report.get("fresh_process_recompute", {}).get("bit_exact", True):
        failures.append({"gate": "fresh_process_recompute", "status": "failed"})
    return {
        "task_id": TASK_ID,
        "producer_function": "uncertainty_voi.runner._failure_manifest",
        "code_path_hash": code_path_hash(_failure_manifest),
        "failures": failures,
        "stop_conditions_triggered": failures,
        "claim_ceiling": CLAIM_CEILING,
    }


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(_json_ready(payload), indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def _write_artifacts(output_dir: Path, payloads: dict[str, Any], trace_rows: Sequence[dict[str, Any]]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in payloads.items():
        if name == "failure_manifest.json" and not payload["failures"]:
            continue
        _write_json(output_dir / name, payload)
    with (output_dir / "trace.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
        for row in trace_rows:
            handle.write(json.dumps(_json_ready(row), sort_keys=True, separators=(",", ":")) + "\n")
    (output_dir / "claim_ceiling.txt").write_text(CLAIM_CEILING + "\n", encoding="utf-8", newline="\n")


def run_gate(
    *,
    cfg: FrozenConfig | None = None,
    output_dir: Path | None = None,
    write_artifacts: bool = True,
    include_fresh_process: bool = False,
) -> dict[str, Any]:
    cfg = cfg or FrozenConfig()
    prereg_sha = sha256_lf(cfg.prereg_path.read_bytes())
    if prereg_sha != EXPECTED_PREREG_SHA256:
        raise RuntimeError(f"frozen prereg SHA mismatch: {prereg_sha}")
    core = _compute_core_payload(cfg)
    if core.get("stopped"):
        if write_artifacts and output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            _write_json(output_dir / "failure_manifest.json", core)
        return core
    core_digest = _payload_digest(_core_for_digest(core))
    replay_report = dict(core["replay_report"])
    if include_fresh_process:
        fresh = _fresh_process_recompute(cfg, core_digest)
        replay_report["fresh_process_recompute"] = fresh
        core["gates"]["G5_replay_rng_trace"]["fresh_process_bit_exact"] = bool(fresh["bit_exact"])
        core["gates"]["G5_replay_rng_trace"]["passed"] = bool(core["gates"]["G5_replay_rng_trace"]["passed"] and fresh["bit_exact"])
        if not fresh["bit_exact"] and core["verdict"] in {"VOI_MECHANISM_PRESENT", "VOI_MECHANISM_PRESENT_UNCALIBRATED"}:
            core["verdict"] = "INSTRUMENT_INVALID"
            core["verdict_subtype"] = "FRESH_PROCESS_RECOMPUTE_FAILED"
            core["positive_claim"] = False
    else:
        replay_report["fresh_process_recompute"] = {
            "fresh_process_recompute_count": 0,
            "bit_exact": True,
            "skipped": True,
        }
    payloads = _build_artifacts_payload(cfg, core, replay_report)
    if write_artifacts:
        _write_artifacts(output_dir or cfg.artifact_dir, payloads, core["trace_rows"])
    return {
        **core,
        "core_digest": core_digest,
        "artifact_payloads": _drop_trace({"payloads": payloads})["payloads"],
        "replay_report": replay_report,
    }


def recompute_core_digest(cfg: FrozenConfig | None = None) -> dict[str, Any]:
    cfg = cfg or FrozenConfig()
    core = _compute_core_payload(cfg)
    if core.get("stopped"):
        digest_payload = core
    else:
        digest_payload = _core_for_digest(core)
    return {
        "task_id": TASK_ID,
        "core_digest": _payload_digest(digest_payload),
        "stopped": bool(core.get("stopped", False)),
        "verdict": core.get("verdict"),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["official", "recompute", "rng-audit"], default="official")
    parser.add_argument("--output", type=Path, default=FrozenConfig().artifact_dir)
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args(argv)
    if args.mode == "rng-audit":
        payload = run_rng_audit()
    elif args.mode == "recompute":
        payload = recompute_core_digest(FrozenConfig())
    else:
        payload = run_gate(cfg=FrozenConfig(), output_dir=args.output, write_artifacts=True, include_fresh_process=True)
        payload = {
            "task_id": TASK_ID,
            "verdict": payload["verdict"],
            "verdict_subtype": payload["verdict_subtype"],
            "positive_claim": payload["positive_claim"],
            "core_digest": payload["core_digest"],
            "trace_size_bytes": payload["trace_size_bytes"],
            "artifact_dir": str(args.output),
        }
    if args.json_output:
        _write_json(args.json_output, payload)
    else:
        print(json.dumps(_json_ready(payload), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
