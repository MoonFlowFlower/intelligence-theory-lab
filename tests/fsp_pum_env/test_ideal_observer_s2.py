import json
from pathlib import Path

import pytest

from src.fsp_pum_env.ideal_observer import (
    ExactBayesFilter,
    FactoredExactFilter,
    PrefixEvent,
    ThetaGridSpec,
    make_fixed_probe_schedules,
    make_s2_variant_wrappers,
    run_factored_equivalence_certificate,
    run_pc_ideal_sanity,
    run_pc_z_sensitivity,
    run_pc_z_sensitivity_addendum,
    run_s2_tractability_benchmark,
    run_s2_tractability_benchmark_v2,
    run_s2_tractability_benchmark_v3,
    run_s2_tractability_benchmark_v4,
    run_z_marginalization_convergence,
    run_z_quadrature_selection_certificate,
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
        filter_seed=20260708,
        variant=SimulatorVariant.CAMOUFLAGE_OFF,
        grid_spec=grid,
        style_map=tuple(range(design["env_parameters"]["renderer"]["response_alphabet_size"])),
    )

    before = filt.posterior_entropy()
    filt.observe(PrefixEvent(action="probe_0", symbol=3))

    assert filt.atom_count == 16
    assert filt.posterior_entropy() < before
    assert filt.posterior_mass() == pytest.approx(1.0, abs=1e-12)


def test_filter_requires_explicit_style_map_and_rejects_true_seed_reuse():
    design = _design()
    grid = ThetaGridSpec.micro_pc_grid(design)

    with pytest.raises(TypeError, match="style_map"):
        ExactBayesFilter(
            design,
            filter_seed=20260708,
            variant=SimulatorVariant.CAMOUFLAGE_OFF,
            grid_spec=grid,
        )

    with pytest.raises(ValueError, match="independent"):
        ExactBayesFilter(
            design,
            filter_seed=20260708,
            true_environment_seed=20260708,
            variant=SimulatorVariant.CAMOUFLAGE_OFF,
            grid_spec=grid,
            style_map=tuple(range(design["env_parameters"]["renderer"]["response_alphabet_size"])),
        )


def test_task_likelihood_uses_z_marginalization_not_filter_seed_replay():
    design = _design()
    grid = ThetaGridSpec.micro_pc_grid(design)
    style = tuple(range(design["env_parameters"]["renderer"]["response_alphabet_size"]))
    args = dict(
        variant=SimulatorVariant.CAMOUFLAGE_OFF,
        grid_spec=grid,
        style_map=style,
        z_quadrature_points=3,
    )
    filt_a = ExactBayesFilter(design, filter_seed=1111, **args)
    filt_b = ExactBayesFilter(design, filter_seed=2222, **args)

    assert filt_a.predict_distribution("task_topic_0") == pytest.approx(
        filt_b.predict_distribution("task_topic_0"), abs=1e-12
    )
    assert filt_a.information_interface()["sees_sampling_seeds"] is False
    assert filt_a.information_interface()["sees_z_realization"] is False


def test_s2_variants_are_thin_wrappers_over_exact_filter_core():
    design = _design()
    grid = ThetaGridSpec.micro_pc_grid(design)
    wrappers = make_s2_variant_wrappers(
        design,
        filter_seed=20260709,
        grid_spec=grid,
        style_map=tuple(range(design["env_parameters"]["renderer"]["response_alphabet_size"])),
        variant=SimulatorVariant.NULL_ENV,
    )

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
    assert all(wrapper.core.variant is SimulatorVariant.NULL_ENV for wrapper in wrappers.values())


def test_policy_wrappers_select_actions_without_second_filter_logic():
    design = _design()
    grid = ThetaGridSpec.micro_pc_grid(design)
    wrappers = make_s2_variant_wrappers(
        design,
        filter_seed=20260709,
        grid_spec=grid,
        style_map=tuple(range(design["env_parameters"]["renderer"]["response_alphabet_size"])),
    )

    assert wrappers["passive"].select_action(0).startswith("task_topic_")
    assert wrappers["fixed_schedule_grid"].select_action(0).startswith("probe_")
    assert wrappers["myopic_IG"].select_action(0).startswith("probe_")
    assert wrappers["ucb1"].select_action(0).startswith("probe_")
    assert all(type(wrapper.core) is ExactBayesFilter for wrapper in wrappers.values())


def test_fixed_probe_grid_implements_all_fifteen_frozen_schedules():
    design = _design()
    schedules = make_fixed_probe_schedules(design)

    assert len(schedules) == 15
    assert {(s.probe_rate, s.placement) for s in schedules} == {
        (rate, placement)
        for rate in (0.0, 0.05, 0.1, 0.2, 0.4)
        for placement in ("front_loaded", "uniform", "back_loaded")
    }
    assert schedules[0].actions_for_episode(design).count("probe_0") == 0
    assert sum(action.startswith("probe_") for action in schedules[-1].actions_for_episode(design)) == 120


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


def test_s2b_artifact_producers_write_required_new_reports(tmp_path):
    convergence = run_z_marginalization_convergence(
        FROZEN,
        output_path=tmp_path / "z_marginalization_convergence.json",
        base_g=3,
    )
    sensitivity = run_pc_z_sensitivity(
        FROZEN,
        output_path=tmp_path / "pc_z_sensitivity_s2b.json",
    )
    tractability = run_s2_tractability_benchmark(
        FROZEN,
        output_path=tmp_path / "s2_tractability_report.json",
        benchmark_turns=12,
        benchmark_queries=4,
    )

    assert convergence["passed"]
    assert convergence["max_abs_prediction_delta"] < 1e-3
    assert sensitivity["passed"]
    assert sensitivity["z_marginalized_mean_log_likelihood"] > sensitivity["wrong_fixed_z_mean_log_likelihood"]
    assert tractability["full_grid_atom_count"] == 7077888
    assert tractability["projected_s5_cpu_hours"] <= 24.0
    assert tractability["decision"] == "tractable"
    assert (tmp_path / "z_marginalization_convergence.json").exists()
    assert (tmp_path / "pc_z_sensitivity_s2b.json").exists()
    assert (tmp_path / "s2_tractability_report.json").exists()


def test_factored_exact_filter_matches_exact_filter_on_preregistered_certificate(tmp_path):
    report_path = tmp_path / "factored_equivalence_certificate.json"

    report = run_factored_equivalence_certificate(FROZEN, output_path=report_path)

    assert report["passed"]
    assert report["max_abs_prediction_delta"] <= 1e-12
    assert {case["case_id"] for case in report["cases"]} == {
        "topic7_flags_trust_432",
        "paired_topic_1_2_trust_432",
    }
    assert json.loads(report_path.read_text(encoding="utf-8")) == report


def test_factored_filter_keeps_joint_log_weight_vector_and_updates_from_real_likelihoods():
    design = _design()
    grid = ThetaGridSpec.micro_pc_grid(design)
    style = tuple(range(design["env_parameters"]["renderer"]["response_alphabet_size"]))
    factored = FactoredExactFilter(
        design,
        filter_seed=20260714,
        variant=SimulatorVariant.CAMOUFLAGE_OFF,
        grid_spec=grid,
        style_map=style,
        z_quadrature_points=5,
    )
    exact = ExactBayesFilter(
        design,
        filter_seed=20260714,
        variant=SimulatorVariant.CAMOUFLAGE_OFF,
        grid_spec=grid,
        style_map=style,
        z_quadrature_points=5,
    )

    assert factored.atom_count == exact.atom_count == 16
    assert factored.log_weights.shape == (16,)
    assert factored.log_weights.dtype.name == "float64"
    assert factored.index_arrays_dtype == "int32"

    event = PrefixEvent(action="probe_3", symbol=18)
    factored.observe(event)
    exact.observe(event)

    assert factored.posterior_mass() == pytest.approx(1.0, abs=1e-12)
    assert factored.predict_distribution("recommend") == pytest.approx(
        exact.predict_distribution("recommend"), abs=1e-12
    )


def test_factored_filter_reports_float64_scatter_kernel_and_stays_exact_on_small_grid():
    design = _design()
    grid = ThetaGridSpec.micro_pc_grid(design)
    style = tuple(range(design["env_parameters"]["renderer"]["response_alphabet_size"]))
    factored = FactoredExactFilter(
        design,
        filter_seed=20260718,
        variant=SimulatorVariant.CAMOUFLAGE_OFF,
        grid_spec=grid,
        style_map=style,
        z_quadrature_points=3,
    )
    exact = ExactBayesFilter(
        design,
        filter_seed=20260718,
        variant=SimulatorVariant.CAMOUFLAGE_OFF,
        grid_spec=grid,
        style_map=style,
        z_quadrature_points=3,
    )

    kernel = factored.scatter_kernel_certificate()
    assert kernel["posterior_storage"] == "unnormalized_float64_log_weight_vector"
    assert kernel["update_kernel"] == "in-place log_weight_vector += log_likelihood_by_class[class_indices]"
    assert kernel["normalization_policy"] == "query-time logsumexp shift; no per-observation normalization"
    assert kernel["approximation"] == "none"
    assert factored.log_weights.dtype.name == "float64"

    for event in (
        PrefixEvent(action="probe_0", symbol=2),
        PrefixEvent(action="task_topic_7", symbol=8),
        PrefixEvent(action="recommend", symbol=13),
    ):
        factored.observe(event)
        exact.observe(event)

    assert factored.posterior_mass() == pytest.approx(1.0, abs=1e-12)
    assert factored.predict_distribution("probe_3") == pytest.approx(
        exact.predict_distribution("probe_3"), abs=1e-12
    )


def test_v2_benchmark_and_z_zero_addendum_write_provenance_reports(tmp_path):
    benchmark = run_s2_tractability_benchmark_v2(
        FROZEN,
        output_path=tmp_path / "s2_tractability_report_v2.json",
        grid_spec=ThetaGridSpec.micro_pc_grid(_design()),
        benchmark_turns=3,
        benchmark_queries=2,
    )
    addendum = run_pc_z_sensitivity_addendum(
        FROZEN,
        output_path=tmp_path / "pc_z_sensitivity_addendum_s2c.json",
    )

    assert benchmark["implementation_path"].startswith("FactoredExactFilter")
    assert benchmark["measured_updates"] == 3
    assert benchmark["measured_counterfactual_queries"] == 2
    assert benchmark["decision_rule"] == "projected_s5_cpu_hours <= 24"
    assert benchmark["full_grid_atom_count"] == 7077888
    assert benchmark["measured_grid_atom_count"] == 16
    assert benchmark["producer_function"] == "src.fsp_pum_env.ideal_observer.run_s2_tractability_benchmark_v2"
    assert addendum["pc_name"] == "PC-Z-SENSITIVITY-Z0-ADDENDUM"
    assert addendum["fixed_z_zero"] == [0.0, 0.0, 0.0]
    assert "z0_fixed_mean_log_likelihood" in addendum
    assert (tmp_path / "s2_tractability_report_v2.json").exists()
    assert (tmp_path / "pc_z_sensitivity_addendum_s2c.json").exists()


def test_s2d_z_selection_certificate_tests_three_and_four(tmp_path):
    report_path = tmp_path / "z_marginalization_convergence_s2d_g_selection.json"

    report = run_z_quadrature_selection_certificate(FROZEN, output_path=report_path)

    assert report["stage"] == "S2d"
    assert report["candidate_g_values"] == [3, 4]
    assert {run["base_g"] for run in report["candidate_runs"]} == {3, 4}
    assert report["threshold"] == 1e-3
    assert report["selected_g"] == min(
        run["base_g"]
        for run in report["candidate_runs"]
        if run["passed"] and run["max_abs_prediction_delta"] < 1e-3
    )
    assert report["selected_node_count"] == report["selected_g"] ** 3
    assert len(report["code_path_hash"]) == 64
    assert json.loads(report_path.read_text(encoding="utf-8")) == report


def test_v3_benchmark_writes_policy_class_cost_note_and_preserves_decision_rule(tmp_path):
    report_path = tmp_path / "s2_tractability_report_v3.json"
    design = _design()

    report = run_s2_tractability_benchmark_v3(
        FROZEN,
        output_path=report_path,
        grid_spec=ThetaGridSpec.micro_pc_grid(design),
        benchmark_turns=3,
        benchmark_queries=2,
        z_quadrature_points=3,
    )

    assert report["artifact"] == "s2_tractability_report_v3"
    assert report["stage"] == "S2d"
    assert report["decision_rule"] == "projected_s5_cpu_hours <= 24"
    assert report["full_grid_atom_count"] == 7077888
    assert report["measured_grid_atom_count"] == 16
    assert report["z_quadrature_points_per_dim"] == 3
    assert report["z_node_count"] == 27
    assert report["scatter_kernel"]["approximation"] == "none"
    assert report["benchmark_scope"]["complete_full_grid_run"] is False
    assert report["policy_class_cost_note"]["policy_class"] == "myopic_IG"
    assert report["policy_class_cost_note"]["probe_actions_evaluated"] == 4
    assert report["policy_class_cost_note"]["measured_wall_clock_seconds"] >= 0.0
    assert report["producer_function"] == "src.fsp_pum_env.ideal_observer.run_s2_tractability_benchmark_v3"
    assert json.loads(report_path.read_text(encoding="utf-8")) == report


def test_s2e_factored_filter_uses_log_domain_updates_and_preserves_exact_queries():
    design = _design()
    grid = ThetaGridSpec.micro_pc_grid(design)
    style = tuple(range(design["env_parameters"]["renderer"]["response_alphabet_size"]))
    factored = FactoredExactFilter(
        design,
        filter_seed=20260719,
        variant=SimulatorVariant.CAMOUFLAGE_OFF,
        grid_spec=grid,
        style_map=style,
        z_quadrature_points=3,
    )
    exact = ExactBayesFilter(
        design,
        filter_seed=20260719,
        variant=SimulatorVariant.CAMOUFLAGE_OFF,
        grid_spec=grid,
        style_map=style,
        z_quadrature_points=3,
    )

    kernel = factored.scatter_kernel_certificate()
    assert kernel["posterior_storage"] == "unnormalized_float64_log_weight_vector"
    assert kernel["update_kernel"] == "in-place log_weight_vector += log_likelihood_by_class[class_indices]"
    assert kernel["normalization_policy"] == "query-time logsumexp shift; no per-observation normalization"
    assert kernel["overflow_bound"]["max_turns"] == 300
    assert kernel["overflow_bound"]["float64_path_can_overflow"] is False
    assert factored.log_weights.dtype.name == "float64"

    for event in (
        PrefixEvent(action="probe_0", symbol=2),
        PrefixEvent(action="task_topic_7", symbol=8),
        PrefixEvent(action="recommend", symbol=13),
    ):
        factored.observe(event)
        exact.observe(event)

    assert factored.posterior_mass() == pytest.approx(1.0, abs=1e-12)
    assert factored.predict_distribution("probe_3") == pytest.approx(
        exact.predict_distribution("probe_3"), abs=1e-12
    )


def test_v4_benchmark_writes_step_profile_and_preserves_decision_rule(tmp_path):
    report_path = tmp_path / "s2_tractability_report_v4.json"
    design = _design()

    report = run_s2_tractability_benchmark_v4(
        FROZEN,
        output_path=report_path,
        grid_spec=ThetaGridSpec.micro_pc_grid(design),
        benchmark_turns=3,
        benchmark_queries=2,
        z_quadrature_points=3,
    )

    assert report["artifact"] == "s2_tractability_report_v4"
    assert report["stage"] == "S2e"
    assert report["decision_rule"] == "projected_s5_cpu_hours <= 24"
    assert report["full_grid_atom_count"] == 7077888
    assert report["measured_grid_atom_count"] == 16
    assert report["step_cost_breakdown"]["after"]["profile_scope"].startswith("one full-grid update step")
    assert "before" in report["step_cost_breakdown"]
    assert report["single_thread_wall_clock_seconds"] == report["measured_wall_clock_seconds"]
    assert report["producer_function"] == "src.fsp_pum_env.ideal_observer.run_s2_tractability_benchmark_v4"
    assert json.loads(report_path.read_text(encoding="utf-8")) == report
