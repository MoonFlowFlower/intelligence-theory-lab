# PROCESS-INTERVENTION-PREFLIGHT-001A Resource Contract

Resource contract:

```text
memory_budget
online_update_budget
lookup_budget
replay_budget
trace_storage_budget
per-step_compute_budget_if_applicable
```

Rules:

```text
witness and controls receive comparable resource budgets
resource_contract_symmetric = true
controls must not be starved
resource use must be reported
resource advantage alone is not mechanism evidence
```

Failure gate:

```text
resource limits starve controls
```
