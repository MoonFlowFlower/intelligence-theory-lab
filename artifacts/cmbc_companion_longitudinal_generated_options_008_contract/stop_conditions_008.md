# Stop Conditions 008

selector_patch_authorized = false

threshold_change_authorized = false

RAG baseline weakening authorized = false

EGO migration = no_go

real companion implementation = not_authorized

proactive messages = not_authorized

LLM action selection = false

Stop with the most specific allowed verdict if future execution shows:

- generated options collapse into a fixed multi-session recipe table
- generator selects, ranks, recommends, or controls final actions
- selector receives non-admitted proposals
- selector receives semantic labels or natural-language descriptions
- selector receives public action names or action family names
- selector receives RAG text, renderer text, or LLM output
- option lifecycle transitions are missing or not replayable
- retired options remain selector-active without reactivation
- near-duplicate options bypass feedback or retirement state
- source deletion has no action-distribution effect
- outcome perturbation has no action-distribution effect
- feedback inheritance is missing
- context-scoped feedback admission fails
- RAG / nearest-neighbor / frequency / recency / heuristic baseline becomes equivalent
- behavior-only replay fails
- admission-aware replay fails
- option-lifecycle replay fails
- renderer adversarial prompt changes selected action
- probes are mutated after results
- 003 / 005 / 006 / 007 evidence is rewritten
