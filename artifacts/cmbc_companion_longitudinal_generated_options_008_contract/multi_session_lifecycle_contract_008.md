# Multi-Session Lifecycle Contract 008

Future execution must show generated CandidateOptions moving through explicit lifecycle states across at least four sessions:

- proposed
- admitted
- active
- deduplicated
- composed
- retired
- reactivated

Each lifecycle transition must include:

- anonymous option ID
- proposal ID
- admission decision ID
- source evidence refs
- context scope
- uncertainty / confidence before and after transition
- selector-visible effect-vector visibility status
- reason code for creation, deduplication, composition, retirement, or reactivation

Retired options must not remain selector-active. Reactivation is allowed only when a new admission decision explicitly points to prior lineage and current context evidence.

Minimum future gates:

```text
session_count >= 4
total_turn_count >= 24
option_creation_event_count >= 4
option_retirement_event_count >= 2
retired_option_selected_rate = 0.0
retired_option_reactivation_traceable = true
```
