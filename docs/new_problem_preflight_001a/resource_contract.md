# NEW-PROBLEM-PREFLIGHT-001A Resource Contract

Resource constraints are allowed only as symmetric accounting.

Future task cards must freeze:

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
witness and controls must receive comparable resource budgets
controls must not be starved
resource limits must be frozen before any run
resource use must be reported, not hidden
resource advantage alone is not mechanism evidence
```

If the only reason cheap controls fail is asymmetric resource starvation, the
future proxy must fail with a resource-asymmetry verdict.
