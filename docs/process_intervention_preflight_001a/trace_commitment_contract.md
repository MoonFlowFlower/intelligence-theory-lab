# PROCESS-INTERVENTION-PREFLIGHT-001A Trace Commitment Contract

## Online Commitment Rule

Future traces must be step-interleaved with environment stepping, append-only,
hash-chained, and committed before verifier outcome or later behavior-probe
results are available. A trace generated after an episode is invalid unless
the task is explicitly evaluating a trace-generator control.

## Required Trace Fields

```text
episode_id
step_id
previous_trace_hash
current_trace_hash
commit_index
system_id
intervention_condition
observation
action
prediction_before_observation
actual_observation
prediction_error_or_update_signal
internal_state_before_update_hash
internal_state_after_update_hash
state_delta_hash
memory_read_keys
memory_write_keys
retrieval_hits
resource_usage
access_manifest
```

## Post-Hoc Detection Requirements

Replay must reject:

```text
non-monotonic commit_index
broken previous_trace_hash to current_trace_hash chain
trace field filled after later behavior probe
verifier outcome used to fill update fields
prior trace records edited without invalidating descendant hashes
```

Failure verdict:

```text
process_intervention_preflight_001a_amendment_001_failed_trace_commitment_missing
```

