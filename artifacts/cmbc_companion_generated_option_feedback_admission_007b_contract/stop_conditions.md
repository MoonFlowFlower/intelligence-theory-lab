# Stop Conditions

Stop with the most specific allowed verdict if any of these appear:

- pending_counterevidence modifies selector-visible predicted_effect_vector
- pending_counterevidence changes action_distribution before admission
- pending feedback creates a high-confidence selector-visible option
- repeated or high-confidence evidence is not required for admission
- context_scope is missing
- global feedback application is used for local timing or intrusive feedback
- option lineage does not inherit pending/admitted feedback state
- selector sees raw feedback deltas
- selector sees semantic labels
- selector sees natural-language descriptions
- selector sees renderer text
- selector sees RAG text or LLM output
- behavior-only replay or admission-aware replay missing
- admission-aware replay cannot reconstruct proposal/admission/context/effect visibility
- thresholds are changed
- RAG / heuristic / nearest-neighbor baselines are weakened
- prior probes are mutated after results
- EGO integration appears
- real companion implementation appears
- proactive messages appear
- LLM action selection appears

Allowed verdicts:

- `generated_option_feedback_admission_007b_contract_ready`
- `contract_incomplete`
- `pending_counterevidence_visibility_unresolved`
- `context_scope_contract_incomplete`
- `admission_aware_replay_contract_incomplete`
- `uncertainty_update_contract_incomplete`
- `boundary_violation`
