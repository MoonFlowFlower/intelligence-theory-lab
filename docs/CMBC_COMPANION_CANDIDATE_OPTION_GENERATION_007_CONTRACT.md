# CMBC Companion Candidate Option Generation 007 Contract

Status: contract-only. No implementation or execution is authorized.

## Decision

`CMBC-COMPANION-PARAMETRIC-ACTION-EXPANSION-006-EXECUTE` passed as bounded N>=20 anonymous CandidateOption evidence:

`parametric_action_expansion_006_bounded_pass`

That result shows the current CMBC lab harness can score a prebuilt expanded anonymous option set. It does not show where open companion behavior options come from, how they are admitted, whether generated options are traceable, or whether a generator can stay out of the control loop.

The next authorized object is only this contract:

`CMBC-COMPANION-CANDIDATE-OPTION-GENERATION-007-CONTRACT`

## Goal

Define a bounded contract for generating, admitting, deduplicating, composing, and retiring anonymous CandidateOptions without allowing the generator, RAG, prompt, renderer, or LLM to become the action selector.

This contract does not implement a generator, does not execute a shadow run, does not patch the selector, and does not authorize real companion behavior.

## Current Claim Ceiling

Current maximum claim:

`CMBC has bounded free-input causal-probe evidence under small and N=24 anonymous CandidateOption spaces. Open option generation is not established.`

This contract cannot prove:

- open-ended companion behavior generation
- scalable real companion behavior control
- real proactive messaging safety
- LLM action selection safety
- EGO readiness
- consciousness
- subjective experience
- true self-awareness
- AGI
- life
- real emotion
- real love

## Required Contract Objects

The contract package defines:

- `CandidateOptionProposal`
- `OptionAdmissionGate`
- `AdmittedCandidateOption`
- `OptionLineageTrace`
- `OptionDeduplicationReport`
- `OptionRetirementReport`
- `OptionCompositionContract`
- `GeneratorSelectorSeparationContract`
- `OptionEvidenceSupportContract`
- `ReplayContractForGeneratedOptions`
- `BaselineContractForGeneratedOptions`

## Core Gates

1. Generator may propose options but cannot select actions.
2. Selector receives only admitted anonymous CandidateOptions.
3. Natural-language descriptions must not be selector-visible.
4. Semantic labels must not be selector-visible.
5. Every admitted option must have lineage and evidence support.
6. Generated options must carry uncertainty when evidence is weak.
7. Replay must reconstruct the option set and distribution.
8. RAG / heuristic / generator baselines must receive equivalent allowed inputs.
9. Outcome updates must affect future generated option admission or scoring.
10. Retired options must be traceable and reversible.

## Selector-Visible Fields

Allowed selector-visible fields:

- anonymous option ID
- allowed observation feature handles
- learned predicted effect vectors
- uncertainty / confidence values derived from allowed experience
- prior support references without names or descriptions
- non-semantic cost / risk / budget features
- public horizon / budget

Forbidden selector-visible fields:

- semantic action labels
- public action names
- action family names
- natural language action descriptions
- generator prompt or rationale
- RAG text
- renderer text
- LLM output
- object / entity names as shortcuts
- task ID, scenario ID, contract ID, cycle ID
- hidden latent state
- hidden future state
- oracle effects
- oracle plans
- evaluator metrics
- expected outputs
- baseline outputs

## Minimum Future Execution Gates

```text
generated_option_count >= 20
admitted_option_count >= 20
generator_selected_action = false
semantic_label_visible_to_selector = false
natural_language_description_visible_to_selector = false
option_lineage_coverage_rate = 1.0
option_replay_match_rate = 1.0
generator_baseline_action_match_rate < 0.5
rag_causal_probe_match_rate < 0.5
expanded_action_nearest_neighbor_match_rate < 0.5
renderer_action_change_rate = 0.0
outcome_update_changes_future_option_distribution = true
```

## Evidence Preservation

003 remains free-input causal-probe evidence under the original small action set.

005 remains N=7 shadow compatibility evidence.

006 remains bounded N=24 anonymous CandidateOption evidence using a prebuilt expanded option set.

007 must not rewrite prior evidence as generated-option evidence. If a future 007 shadow or execution passes, it must be recorded as new bounded evidence.

## Stop Conditions

Stop with `boundary_violation` or a more specific allowed verdict if the contract or future execution requires any of:

- generator directly selects actions
- selector receives non-admitted proposals
- selector receives natural-language descriptions
- selector receives semantic labels
- selector receives public action names
- selector receives renderer text
- selector receives RAG text or LLM output
- admitted options lack lineage
- admitted options lack evidence support
- weak evidence creates high-confidence options
- replay cannot reconstruct generated option set and full distribution
- baselines receive weaker inputs than CMBC
- retired options are not traceable or reversible
- threshold retuning
- RAG baseline weakening
- EGO integration
- real companion implementation
- proactive messages
- LLM action selection

## Allowed Verdicts

- `candidate_option_generation_contract_ready`
- `generator_selector_boundary_incomplete`
- `semantic_leak_risk_unresolved`
- `option_lineage_contract_incomplete`
- `generated_option_replay_contract_incomplete`
- `baseline_contract_incomplete`
- `boundary_violation`

## Recommended Next Task

If ready, the recommended next task is:

`CMBC-COMPANION-CANDIDATE-OPTION-GENERATION-007-SHADOW`

That task is not authorized by this contract.
