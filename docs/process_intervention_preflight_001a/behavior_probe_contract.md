# PROCESS-INTERVENTION-PREFLIGHT-001A Behavior Probe Contract

## Probe Schema

Each future behavior probe must freeze:

```text
probe_id
probe_name
when_measured_after_intervention
horizon
contexts
paired_comparison_design
baseline_episode
intervened_episode
non_intervened_twin_episode
measured_behavior
effect_size_formula
minimum_effect_size
aggregation_rule
failure_condition
```

## Required Probe Types

```text
future_action_distribution_shift
future_policy_choice_change
future_prediction_change
future_error_recovery_change
future_intervention_probe_response
```

Default minimum effect size:

```text
absolute paired behavior delta >= 0.10 after normalization
```

Failure conditions:

```text
trace changes but behavior does not change
behavior changes but change is matched by fair cheap control
effect size below frozen threshold
effect appears only under post-hoc-selected probe
```

