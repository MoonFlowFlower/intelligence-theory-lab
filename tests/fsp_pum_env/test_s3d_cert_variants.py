from pathlib import Path

import pytest

from src.fsp_pum_env.ideal_observer import ExactBayesFilter, ThetaGridSpec
from src.fsp_pum_env.simulator import FspPumSimulator, SimulatorVariant, contains_latent_leak


FROZEN = Path(__file__).resolve().parents[2] / "artifacts" / "FSP-PUM-ENV-IDPROBE-001A" / "frozen_design.json"


@pytest.mark.parametrize(
    ("variant", "target_symbol"),
    [
        ("degenerate_should_win_constant_none", 0),
        ("degenerate_should_win_constant_saturated", 31),
    ],
)
def test_s3d_cert_only_constant_variants_are_concentrated_theta_independent_and_prefix_clean(variant, target_symbol):
    sim = FspPumSimulator.from_frozen_design(FROZEN, master_seed=20260711, variant=variant)
    style = tuple(range(sim.alphabet_size))
    theta_controls = [
        {
            "sensitivity_flags": [0, 0],
            "topic_values": [-1.5] * 8,
            "trust_gain_alpha": 0.05,
            "trust_decay_beta": 0.9,
            "disclosure_threshold_d": 0.3,
        },
        {
            "sensitivity_flags": [1, 1],
            "topic_values": [1.5] * 8,
            "trust_gain_alpha": 0.2,
            "trust_decay_beta": 0.98,
            "disclosure_threshold_d": 0.7,
        },
        {
            "sensitivity_flags": [1, 0],
            "topic_values": [-1.5, -0.5, 0.5, 1.5, -1.5, -0.5, 0.5, 1.5],
            "trust_gain_alpha": 0.1,
            "trust_decay_beta": 0.95,
            "disclosure_threshold_d": 0.5,
        },
    ]
    users = [sim.start_user(user_id=index, controlled_theta=theta, style_map=style) for index, theta in enumerate(theta_controls)]

    for action in sim.all_actions:
        reference = sim.response_distribution(users[0], action)
        assert reference[target_symbol] >= 0.95
        assert sum(reference) == pytest.approx(1.0, abs=1e-12)
        for user in users[1:]:
            assert sim.response_distribution(user, action) == pytest.approx(reference, abs=1e-9)

    counts = {target_symbol: 0}
    user = sim.start_user(user_id=77, controlled_theta=theta_controls[-1], style_map=style)
    for step in range(10_000):
        if step and step % sim.design["env_parameters"]["episodes"]["total_turns_per_user"] == 0:
            user = sim.start_user(user_id=77 + step, controlled_theta=theta_controls[-1], style_map=style)
        result = sim.step(user, sim.all_actions[step % len(sim.all_actions)])
        assert set(result.observation) == {"symbol"}
        assert not contains_latent_leak(result.to_public_dict())
        counts[target_symbol] += int(result.observation["symbol"] == target_symbol)
    assert counts[target_symbol] / 10_000 >= 0.95


@pytest.mark.parametrize(
    ("variant", "target_symbol"),
    [
        ("degenerate_should_win_constant_none", 0),
        ("degenerate_should_win_constant_saturated", 31),
    ],
)
def test_s3d_cert_only_constant_variants_match_exact_filter_on_micro_grid(variant, target_symbol):
    sim = FspPumSimulator.from_frozen_design(FROZEN, master_seed=20260712, variant=variant)
    style = tuple(range(sim.alphabet_size))
    user = sim.start_user(user_id=3, style_map=style)
    filt = ExactBayesFilter.from_frozen_design(
        FROZEN,
        filter_seed=20260799,
        true_environment_seed=20260712,
        variant=variant,
        style_map=style,
        grid_spec=ThetaGridSpec.micro_pc_grid(sim.design),
        user_id=3,
        z_quadrature_points=3,
    )

    for action in ("task_topic_0", "probe_0", "recommend", "task_topic_7"):
        assert filt.predict_distribution(action) == pytest.approx(sim.response_distribution(user, action), abs=1e-9)
        result = sim.step(user, action)
        filt.observe({"action": action, "observation": result.observation})
        assert filt.predict_distribution(action)[target_symbol] >= 0.95
