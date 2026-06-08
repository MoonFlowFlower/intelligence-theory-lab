# Update Ordering Contract

Source RCA: `outcome_update_ordering_bug_confirmed`.

The required update ordering is:

```text
feedback event
-> feedback attribution
-> PendingCounterevidenceRecord or admitted feedback candidate
-> FeedbackAdmissionState
-> AdmissionFilteredEffectVector
-> selector-visible CandidateOption payload
-> action distribution
```

Rules:

- pending_counterevidence MUST NOT modify selector-visible predicted_effect_vector.
- pending_counterevidence may only update pending evidence state, uncertainty, confidence, and context-local admission state.
- admitted_context_counterevidence may modify selector-visible predicted_effect_vector only after the admission requirements are satisfied.
- selector input must use an admission-filtered effect vector.
- raw feedback deltas and pending effect deltas must remain outside selector-visible fields.
- outcome update must not change future option distribution before admission filtering.

Failure to prove this ordering is a contract failure, not a selector success.
