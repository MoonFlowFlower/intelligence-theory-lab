# PROCESS-INTERVENTION-PREFLIGHT-001A State Accounting Contract

## Trace Write-Only Rule

Trace fields are write-only audit outputs. Systems may not use prior trace
records as working memory unless the future executable task explicitly permits
that access and counts it against the same memory budget as all other memory.

## Budget Accounting

```text
serialized_internal_state_before_update counts against state_budget
serialized_internal_state_after_update counts against state_budget
any trace information that influences future behavior counts against memory_budget
memory_read_keys and memory_write_keys count against memory operation budget
retrieval_hits must be reproducible from declared memory state
```

Failure verdict:

```text
process_intervention_preflight_001a_amendment_001_failed_trace_hidden_memory
```

