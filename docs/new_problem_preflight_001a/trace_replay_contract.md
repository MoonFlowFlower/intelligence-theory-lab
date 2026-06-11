# NEW-PROBLEM-PREFLIGHT-001A Trace / Replay Contract

Future trace records must include at least:

```text
episode_id
step_id
observation
action
allowed_history
intervention_condition
counterfactual_action_probe
prediction_before_action
action_conditioned_prior_or_state_before_observation
actual_observation
prediction_error_or_update_signal
internal_state_before_update
internal_state_after_update
state_delta
memory_read_keys
memory_write_keys
retrieval_hits
ablation_condition
resource_usage
system_output
future_behavior_probe
verifier_label_or_outcome
access_manifest
lineage_id
```

Future replay must verify:

```text
same traces reproduce same metrics
non-oracle systems did not access forbidden data
internal state changed only through allowed update path
behavior changes after deletion/intervention are traceable
cheap controls received fair access
graph/cache/kNN/summary/FSM controls were not disabled
trace-only replay cannot reproduce both trace and future behavior
behavior-only replay cannot reproduce intervention response
```

If trace-only replay can reproduce both trace and future behavior, a positive
mechanism claim is invalid.
