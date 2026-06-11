# PROCESS-INTERVENTION-PREFLIGHT-001A Trace Replay Contract

Future trace schema:

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

Future failure gates:

```text
trace-only replay matches trace + behavior
behavior-only replay matches intervention response
graph/cache trace generator matches trace + behavior
post-hoc trace generation explains the evidence
```
