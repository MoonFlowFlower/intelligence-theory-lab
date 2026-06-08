# Stop Conditions

Stop with the most specific allowed verdict if any future redteam execution shows:

- fixed recipe generator or fixed hidden option table
- generator selects, ranks, recommends, or controls final action
- selector receives non-admitted proposals
- selector receives semantic labels
- selector receives natural-language descriptions
- selector receives public action names
- selector receives action family names
- selector receives RAG text
- selector receives renderer text
- selector receives LLM output
- admission gate always passes or always rejects
- weak evidence creates high-confidence selector-visible options
- pending counterevidence changes selector-visible effect vector before admission
- near-duplicate options bypass feedback admission state
- missing or falsified lineage is not detected
- replay cannot reconstruct generated option proposals, admissions, lineage, perturbation, and full distribution
- RAG / heuristic / nearest-neighbor / frequency / recency baseline becomes equivalent under causal probes
- supporting lineage deletion has no distribution effect
- outcome perturbation has no distribution effect
- renderer adversarial prompt changes selected option
- selector thresholds are changed
- baselines are weakened or made incomparable
- probes are mutated after results
- failed 007-EXECUTE or prior evidence is rewritten as pass evidence
- EGO integration appears
- real companion implementation appears
- proactive messages appear
- LLM action selection appears

Allowed verdicts:

- `generated_option_007_redteam_contract_ready`
- `contract_incomplete`
- `fake_generator_risk_unresolved`
- `generator_hidden_selector_risk_unresolved`
- `admission_gate_contract_incomplete`
- `lineage_replay_contract_incomplete`
- `baseline_contract_incomplete`
- `semantic_leak_risk_unresolved`
- `boundary_violation`

