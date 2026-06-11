# PROCESS-INTERVENTION-PREFLIGHT-001A Separation Statistic Contract

## Purpose

The future task must not pass because a witness has intervention response,
internal update trace, and later behavior change. Honest online cheap controls
can also satisfy those three. The future task must freeze a statistic that
compares update dynamics against fair online controls.

## Primary Statistic

not output accuracy alone

```text
statistic_name = resource_normalized_heldout_composition_update_divergence
hypothesis = witness update dynamics retain heldout intervention composition structure better than fair online cheap controls under the same access and resource contract
formula = mean_heldout(delta_behavior_after_update * update_path_replay_validity) / max(1, normalized_resource_usage)
required_trace_fields = intervention_condition, prediction_error_or_update_signal, state_delta_hash, memory_read_keys, memory_write_keys, retrieval_hits, resource_usage
required_interventions = all eight required intervention families plus heldout pairwise compositions
cheap-control_comparison_set = all required online controls and intervention_labeled_graph_cache
equivalence_band = absolute statistic difference <= 0.05
pass_threshold = witness exceeds best fair online control by > 0.10 after resource normalization
fail_threshold = best fair online control within equivalence_band or above witness
seed_aggregation_rule = median seed margin > 0.10 and lower 95 percent bootstrap confidence bound > 0.05
expected_cheap-control_collapse_mode = online table, graph, kNN, or FSM stores intervention-conditioned transition/update entries
why_not_output_accuracy_alone = requires replay-valid update path and heldout intervention composition, not only correct probe output
why_not_arbitrary_trace_distance = uses predeclared fields, resource normalization, and paired behavior effect
```

## Secondary Diagnostics

```text
statistic_name = prediction_error_causal_use_profile
purpose = prediction-error injection/removal must change both update path and later behavior
fail_if = prediction error is logged but removal does not change later behavior
```

```text
statistic_name = deletion_sensitivity_profile
purpose = declared memory writes and state deltas must be causally exposed by deletion or freezing
fail_if = deletion targets decorative keys or fair online controls match the profile
```

If the best fair online cheap control matches the witness on the frozen
primary statistic, the future executable preflight fails.
