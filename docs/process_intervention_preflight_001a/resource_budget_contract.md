# PROCESS-INTERVENTION-PREFLIGHT-001A Resource Budget Contract

## Frozen Budget Template

The future executable task must freeze numeric or structural budgets. Default
001B draft budgets are:

```text
episode_count = 96 total paired episodes
intervention_count = 8 base families plus 8 heldout pairwise compositions
training_history_budget = 64 episodes
online_history_budget = 32 episodes
memory_budget = 128 key-value entries, each <= 256 bytes
state_budget = 16 KiB serialized state per system step
trace_storage_budget = unbounded write-only audit output for all systems
online_update_budget = one update call per environment step
lookup_budget = 128 key reads or graph traversals per step
replay_budget = one deterministic replay per system per frozen seed
per_step_compute_budget_if_applicable = 100000 primitive operations or declared unbounded for all systems
```

If any budget is changed before execution, the Stage0 freeze manifest must
record the change before the first verifier run.

## Starvation Check

Each required control must pass a competence calibration task inside the frozen
budget. If a required control fails calibration because the budget starves it,
the future executable task fails by resource asymmetry.

Failure verdicts:

```text
process_intervention_preflight_001a_amendment_001_failed_resource_budget_unspecified
process_intervention_preflight_001a_amendment_001_failed_control_starvation
```

