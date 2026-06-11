# PROCESS-INTERVENTION-PREFLIGHT-001A Match Metric Contract

## Frozen Metric Families

No post-hoc metric selection

The future executable task must freeze all metric formulas before any run. No
post-hoc metric selection or threshold tuning is allowed. No post-hoc metric
selection is valid evidence.

## Primary Match Metrics

```text
metric_name = intervention_response_match
formula = 1 - normalized_distance(response_vector_candidate, response_vector_control)
input_fields = intervention_id, paired_control_episode, action, prediction_before_observation, actual_observation
normalization = per-intervention max possible categorical or scalar distance
equivalence_band = distance <= 0.05
threshold = match_rate >= 0.95
aggregation_rule = mean over intervention families and heldout compositions
seed_aggregation_rule = lower 95 percent bootstrap confidence bound >= threshold
tie_break_rule = fair cheap control match forces failure
failure_verdict_if_matched = process_intervention_preflight_001b_failed_control_intervention_response_match
```

```text
metric_name = internal_update_trace_match
formula = 1 - normalized_distance(update_signature_candidate, update_signature_control)
input_fields = prediction_error_or_update_signal, state_delta_hash, memory_read_keys, memory_write_keys, retrieval_hits
normalization = edit distance over committed update-event signatures
equivalence_band = distance <= 0.10
threshold = match_rate >= 0.90
aggregation_rule = mean over committed steps with interventions
seed_aggregation_rule = lower 95 percent bootstrap confidence bound >= threshold
tie_break_rule = fair cheap control match forces failure
failure_verdict_if_matched = process_intervention_preflight_001b_failed_control_update_trace_match
```

```text
metric_name = later_behavior_change_match
formula = 1 - normalized_distance(behavior_delta_candidate, behavior_delta_control)
input_fields = future_behavior_probe, baseline_episode, intervened_episode, non_intervened_twin_episode
normalization = per-probe effect-size range
equivalence_band = distance <= 0.05
threshold = match_rate >= 0.95
aggregation_rule = mean over probe families and horizons
seed_aggregation_rule = lower 95 percent bootstrap confidence bound >= threshold
tie_break_rule = fair cheap control match forces failure
failure_verdict_if_matched = process_intervention_preflight_001b_failed_control_later_behavior_match
```

## Solve Definition

```text
match = metric distance inside frozen equivalence_band
reproduce = match all three primary metrics on the same frozen split
solve = reproduce and match the primary separation statistic
```

If the best fair online cheap control solves under this definition, the future
executable preflight fails.
