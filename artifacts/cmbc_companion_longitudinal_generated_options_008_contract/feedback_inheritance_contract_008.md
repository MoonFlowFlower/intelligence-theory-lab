# Feedback Inheritance Contract 008

Generated options must inherit relevant pending and admitted feedback state from their source lineage. A new anonymous option ID cannot erase:

- pending counterevidence
- admitted context counterevidence
- uncertainty penalties
- context scope restrictions
- retired lineage state

Context-local feedback must not become global. If a user correction narrows context, descendant options must inherit the narrowed scope rather than the broader preliminary scope.

Minimum future gates:

```text
feedback_inheritance_coverage_rate = 1.0
context_scoped_feedback_admission_rate = 1.0
single_contradiction_status = pending_counterevidence
repeated_context_matched_feedback_status = admitted_context_counterevidence
near_duplicate_bypass_rate = 0.0
```

Stop if a near-duplicate generated option bypasses pending or admitted feedback state by receiving a fresh anonymous option ID.
