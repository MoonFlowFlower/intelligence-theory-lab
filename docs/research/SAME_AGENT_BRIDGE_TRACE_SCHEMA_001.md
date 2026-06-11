# SAME_AGENT_BRIDGE_TRACE_SCHEMA_001

Task: SAME-AGENT-BRIDGE-GOVERNANCE-001-FIXA
Mode: schema contract only. No implementation.

This file defines the canonical state and trace/replay fields for future
same-agent Gate0-to-Gate1 bridge tasks.

## Canonical Agent State Schema

Every same-agent bridge run must expose a canonical state snapshot with these
minimum fields.

```json
{
  "agent_id": "stable same-agent identifier for the run family",
  "schema_version": "same_agent_bridge_trace_schema_001",
  "episode_id": "episode identifier",
  "step_id": "monotonic step identifier",
  "state_snapshot_id": "required state snapshot id",
  "parent_state_snapshot_id": "previous state snapshot id or null",
  "state_hash": "hash of canonical serialized state snapshot",
  "parent_state_hash": "previous state hash or null",
  "belief_state": {},
  "action_conditioned_prior": {},
  "observation_posterior": {},
  "prediction_error": {},
  "episodic_trace": [],
  "replay_event": null,
  "consolidated_model_delta": null,
  "policy_delta": null,
  "decision_reason_source": "mechanism | baseline | ablation | replay | unknown",
  "self_boundary_state": {
    "status": "placeholder_not_implemented",
    "allowed_use": "schema reservation only"
  },
  "value_state": {
    "status": "placeholder_not_implemented",
    "allowed_use": "schema reservation only"
  }
}
```

A shared `agent_id` string alone is insufficient. Same-agent continuity must be
verified through schema versioning, parent/child state snapshot IDs, state
hashes, and replayable transition records.

## Canonical Trace/Replay Record

Each step trace must include at minimum:

```json
{
  "agent_id": "required",
  "schema_version": "same_agent_bridge_trace_schema_001",
  "episode_id": "required",
  "step_id": "required",
  "state_snapshot_id": "required",
  "parent_state_snapshot_id": "required except initial state",
  "state_hash": "required",
  "parent_state_hash": "required except initial state",
  "observation": {},
  "action": {},
  "belief_before": {},
  "action_conditioned_prior": {},
  "predicted_outcome": {},
  "actual_outcome": {},
  "prediction_error": {},
  "belief_after": {},
  "memory_write": null,
  "replay_event": null,
  "consolidated_model_delta": null,
  "policy_delta": null,
  "decision_reason_source": "mechanism | baseline | ablation | replay | unknown"
}
```

Replay records must be reconstructable from frozen trace records. A replay
event must not depend on hidden runtime objects that are absent from the trace,
unless the task card explicitly declares those objects and includes a runtime
access manifest.

## State Lineage Chain

Every implementation must emit either:

- a state lineage hash chain, or
- a hash-chain-equivalent record that allows each state transition to be
  replayed and verified from the previous state hash.

The chain must cover initial state, Gate 0 contract trace production, replay or
consolidation events, ablations, baseline arms, and held-out evaluation states.

## Trace Causality Requirements

For bridge evidence, the trace must show:

- the Gate 0 action-conditioned prediction-error record existed before Gate 1
  replay/consolidation used it
- the replay/consolidation event identifies the source trace IDs
- the consolidated model delta or policy delta is logged after the replay event
- held-out evaluation happens after the claimed delta
- ablations can remove or corrupt the source trace without changing unrelated
  runtime paths
- state lineage links the claimed same agent across these transitions

## Schema Fragmentation Rule

Any future task that changes required field names, omits required fields, moves
critical evidence into a renderer, or creates a test-only schema must declare a
schema migration before execution.

Correct verdict handling:

```text
verdict = fail or blocked
failure_taxonomy_labels includes schema_fragmentation
```

The verdict itself must remain compatible with:

```text
pass
fail
blocked
inconclusive
```

## What This Schema Does Not Prove

This schema does not implement self-boundary, value, agency, consciousness,
subjective experience, emotion, or companion behavior. The placeholder fields
are reservations for future explicit task cards only.
