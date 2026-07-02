import math
from pathlib import Path

import pytest

from src.fsp_pum_env.simulator import (
    FspPumSimulator,
    SimulatorVariant,
    contains_latent_leak,
)


FROZEN = Path(__file__).resolve().parents[2] / "artifacts" / "FSP-PUM-ENV-IDPROBE-001A" / "frozen_design.json"


def _base_sim(seed=20260701, variant=SimulatorVariant.BASE):
    return FspPumSimulator.from_frozen_design(FROZEN, master_seed=seed, variant=variant)


def _uniform_distance(distribution):
    expected = 1.0 / len(distribution)
    return sum(abs(p - expected) for p in distribution)


def test_distributional_sanity_uses_frozen_design_and_discrete_symbol_surface():
    sim = _base_sim()
    user = sim.start_user(user_id=7)

    assert sim.alphabet_size == 32
    assert len(sim.task_actions) == 8
    assert len(sim.probe_actions) == 4
    assert sim.theta_topic_levels == (-1.5, -0.5, 0.5, 1.5)
    assert sim.interaction_pairs == ((1, 2), (5, 6))
    assert sorted(user.style_map) == list(range(sim.alphabet_size))

    symbols = []
    for step in range(24):
        action = sim.task_actions[step % len(sim.task_actions)]
        result = sim.step(user, action)
        symbols.append(result.observation["symbol"])
        assert set(result.observation) == {"symbol"}
        assert 0 <= result.observation["symbol"] < sim.alphabet_size
        assert result.cost_metering["tokens_per_turn_proxy"] == 1
        assert result.cost_metering["probe_trust_cost"] == 0.0

    assert len(set(symbols)) > 1
    assert math.isclose(sum(sim.response_distribution(user, "task_topic_3")), 1.0, rel_tol=0, abs_tol=1e-12)


def test_probe_actions_reduce_observation_informativeness_via_trust_direction():
    task_sim = _base_sim(seed=20260702)
    probe_sim = _base_sim(seed=20260702)
    task_user = task_sim.start_user(user_id=11)
    probe_user = probe_sim.start_user(user_id=11)

    for _ in range(18):
        task_sim.step(task_user, "task_topic_0")
        probe_sim.step(probe_user, "probe_3")

    task_distance = _uniform_distance(task_sim.response_distribution(task_user, "task_topic_4"))
    probe_distance = _uniform_distance(probe_sim.response_distribution(probe_user, "task_topic_4"))

    assert task_distance > probe_distance


def test_probe_only_dimensions_are_silent_for_passive_actions_at_interface():
    sim = _base_sim(seed=20260703)
    low_probe_user = sim.start_user(
        user_id=21,
        controlled_theta={
            "sensitivity_flags": [0, 0],
            "topic_values": [-0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, -1.5],
        },
    )
    high_probe_user = sim.start_user(
        user_id=21,
        controlled_theta={
            "sensitivity_flags": [1, 1],
            "topic_values": [-0.5, 0.5, -0.5, 0.5, -0.5, 0.5, -0.5, 1.5],
        },
        style_map=low_probe_user.style_map,
    )

    for action in ("task_topic_0", "task_topic_3", "recommend"):
        assert sim.response_distribution(low_probe_user, action) == pytest.approx(
            sim.response_distribution(high_probe_user, action), abs=1e-12
        )

    assert sim.response_distribution(low_probe_user, "probe_3") != pytest.approx(
        sim.response_distribution(high_probe_user, "probe_3"), abs=1e-12
    )


def test_theta_and_z_never_serialize_into_observation_or_step_result_structures():
    sim = _base_sim(seed=20260704)
    user = sim.start_user(user_id=31)
    result = sim.step(user, "probe_0")

    assert result.observation == {"symbol": result.observation["symbol"]}
    assert not contains_latent_leak(result.observation)
    assert not contains_latent_leak(result.to_public_dict())


@pytest.mark.parametrize("variant", list(SimulatorVariant))
def test_all_knob_variants_use_same_generator_surface_and_step_cleanly(variant):
    sim = _base_sim(seed=20260705, variant=variant)
    assert type(sim) is FspPumSimulator

    user = sim.start_user(user_id=41)
    result = sim.step(user, "probe_1")

    assert set(result.observation) == {"symbol"}
    assert 0 <= result.observation["symbol"] < sim.alphabet_size
    assert math.isclose(sum(sim.response_distribution(user, "recommend")), 1.0, rel_tol=0, abs_tol=1e-12)


def test_planted_leak_mutant_is_caught_by_structural_scaffold():
    clean = {"symbol": 3, "cost_metering": {"probe_trust_cost": 0.08}}
    planted = {"symbol": 3, "debug": {"theta": [1.5]}}
    planted_z = {"symbol": 3, "latent_state": {"z": {"stress": 0.4}}}

    assert not contains_latent_leak(clean)
    assert contains_latent_leak(planted)
    assert contains_latent_leak(planted_z)
