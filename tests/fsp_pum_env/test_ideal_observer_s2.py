import json
from pathlib import Path

import pytest

from src.fsp_pum_env.ideal_observer import (
    ExactBayesFilter,
    PrefixEvent,
    ThetaGridSpec,
    make_s2_variant_wrappers,
    run_pc_ideal_sanity,
)
from src.fsp_pum_env.simulator import SimulatorVariant


FROZEN = Path(__file__).resolve().parents[2] / "artifacts" / "FSP-PUM-ENV-IDPROBE-001A" / "frozen_design.json"


def _design():
    return json.loads(FROZEN.read_text(encoding="utf-8-sig"))


def test_prefix_event_is_public_action_observation_only():
    event = PrefixEvent.from_mapping({"action": "probe_0", "observation": {"symbol": 3}})

    assert event == PrefixEvent(action="probe_0", symbol=3)

    with pytest.raises(ValueError, match="prefix-only"):
        PrefixEvent.from_mapping({"action": "probe_0", "observation": {"symbol": 3}, "theta": [1.5]})

    with pytest.raises(ValueError, match="prefix-only"):
        PrefixEvent.from_mapping({"action": "probe_0", "observation": {"latent_state": {"z": 0.0}}})

    with pytest.raises(ValueError, match="symbol"):
        PrefixEvent.from_mapping({"action": "probe_0", "observation": {"not_symbol": 3}})


def test_exact_filter_updates_posterior_from_prefix_events_without_hidden_state():
    design = _design()
    grid = ThetaGridSpec.micro_pc_grid(design)
    filt = ExactBayesFilter(
        design,
        master_seed=20260708,
        variant=SimulatorVariant.CAMOUFLAGE_OFF,
        grid_spec=grid,
    )

    before = filt.posterior_entropy()
    filt.observe(PrefixEvent(action="probe_0", symbol=3))

    assert filt.atom_count == 16
    assert filt.posterior_entropy() < before
    assert filt.posterior_mass() == pytest.approx(1.0, abs=1e-12)


def test_s2_variants_are_thin_wrappers_over_exact_filter_core():
    design = _design()
    grid = ThetaGridSpec.micro_pc_grid(design)
    wrappers = make_s2_variant_wrappers(design, master_seed=20260709, grid_spec=grid)

    assert set(wrappers) == {
        "full_history",
        "truncation_B30",
        "passive",
        "myopic_IG",
        "fixed_schedule_grid",
        "ucb1",
    }
    assert all(type(wrapper.core) is ExactBayesFilter for wrapper in wrappers.values())
    assert wrappers["truncation_B30"].history_limit == 30
    assert wrappers["full_history"].history_limit is None


def test_policy_wrappers_select_actions_without_second_filter_logic():
    design = _design()
    grid = ThetaGridSpec.micro_pc_grid(design)
    wrappers = make_s2_variant_wrappers(design, master_seed=20260709, grid_spec=grid)

    assert wrappers["passive"].select_action(0).startswith("task_topic_")
    assert wrappers["fixed_schedule_grid"].select_action(0).startswith("probe_")
    assert wrappers["myopic_IG"].select_action(0).startswith("probe_")
    assert wrappers["ucb1"].select_action(0).startswith("probe_")
    assert all(type(wrapper.core) is ExactBayesFilter for wrapper in wrappers.values())


def test_pc_ideal_sanity_writes_provenance_and_wall_clock(tmp_path):
    report_path = tmp_path / "pc_ideal_sanity.json"

    report = run_pc_ideal_sanity(FROZEN, output_path=report_path, master_seed=20260710)

    assert report["pc_ideal_sanity"] >= 0.95
    assert report["threshold"] == 0.95
    assert report["producer_function"] == "src.fsp_pum_env.ideal_observer.run_pc_ideal_sanity"
    assert report["input_artifacts"] == [str(FROZEN)]
    assert report["atom_count"] == 16
    assert report["wall_clock_seconds"] >= 0.0
    assert report["mean_entropy_drop"] > 0.0
    assert len(report["code_path_hash"]) == 64
    assert report["claim_ceiling"] == "PC-IDEAL-SANITY instrument evidence only"
    assert json.loads(report_path.read_text(encoding="utf-8")) == report
