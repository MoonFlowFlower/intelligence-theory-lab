# CMBC Companion Parametric Action Interface 005 Contract

Status: contract-only. No implementation or execution is authorized.

## Decision

`CMBC-COMPANION-ACTION-SPACE-EXPANSION-004-RCA` confirmed:

`selector_static_action_handle_bottleneck_confirmed`

The frozen selector is not parametric over candidate action space. It iterates the existing 7 `ACTION_HANDLES` and has no `candidate_options` input.

The next authorized object is only this contract:

`CMBC-COMPANION-PARAMETRIC-ACTION-INTERFACE-005-CONTRACT`

## Goal

Define a parametric anonymous `CandidateOption` interface so a future CMBC selector can be tested over variable-N candidate option lists without semantic label leaks, renderer control, threshold retuning, baseline weakening, or rewriting prior 003 evidence.

This contract does not implement the selector. It defines the public interface, trace schema, replay contract, baseline contract, renderer adapter boundary, and evidence preservation rules required before a future shadow implementation can be reviewed.

## Current Claim Ceiling

Current maximum claim:

`CMBC has bounded free-input causal-probe evidence under the current small 7-action anonymous action set. Expanded action-space advantage is not established because the frozen selector is not parametric over action space.`

This contract cannot prove:

- expanded action-space causal-probe advantage
- scalable companion behavior control
- open-ended action generation
- live human trial robustness
- real companion agent readiness
- real proactive messaging safety
- LLM renderer safety in production
- EGO readiness
- consciousness
- subjective experience
- true self-awareness
- AGI
- life
- real emotion
- real love

## Required Interface Objects

- `CandidateOption`
- `ParametricSelectorInput`
- `PredictionBeforeActionPerOption`
- `ActionDistributionOverOptions`
- `ParametricReplayTrace`
- `PostSelectionRendererAdapter`
- `ExpandedBaselineInput`
- `7-action shadow adapter`
- evidence preservation contract for 003

## Selector-Visible Fields

Allowed selector-visible fields:

- public observation features
- anonymous option IDs
- own-intervention history
- observed outcomes
- learned predicted effect vectors
- uncertainty / confidence values derived from allowed experience
- non-semantic goal / constraint vectors
- public horizon / budget
- prior support references without semantic labels
- non-semantic cost / risk / budget features

Forbidden selector-visible fields:

- semantic action labels
- public action names
- action family names
- natural language action descriptions
- rendered text
- renderer prompts
- object / entity names as shortcuts
- task ID, scenario ID, contract ID, cycle ID
- hidden latent state
- hidden future state
- oracle action-to-effect table
- oracle plans
- evaluator metrics
- expected outputs
- baseline outputs

## Variable-N Contract

The future selector interface must consume:

```text
ParametricSelectorInput {
  observation
  candidate_options: list[CandidateOption]
  own_intervention_history
  observed_outcomes
  goal_constraint_vector
  public_horizon
  public_budget
}
```

`candidate_options` must support:

- `N = 7` for shadow compatibility with current evidence
- `N >= 20` for future action-space expansion execution
- variable N without code branches such as `if N == 7`

The future selector must output:

```text
PredictionBeforeActionPerOption
ActionDistributionOverOptions
selected_option_id
```

## 7-Action Shadow Adapter

The shadow adapter exists only to test whether the new interface can reproduce current small-action evidence without rewriting it.

Rules:

- It may map each existing small action to one anonymous `CandidateOption`.
- It must not expose public action names or semantic families to selector input.
- It must not rewrite 003 as parametric evidence.
- Do not rewrite 003 as parametric evidence.
- It must record old trace IDs as preserved lineage, not new proof.
- It must fail if adapter output changes prior 003 replay decisions without a declared reason.

## Future N>=20 Execution Path

A future execution can be considered only after human review authorizes a shadow implementation task. That future execution must:

- freeze selector, adapter, renderer, baselines, thresholds, and probes before running
- use at least 20 and at most 50 anonymous candidate options
- run label permutation and effect swap
- run supporting-prior deletion and outcome perturbation
- run behavior-only replay from the full option distribution
- run expanded baselines on the same anonymous options
- keep renderer strictly post-selection

## Stop Conditions

Stop immediately and return `boundary_violation` if the contract requires any of:

- `ACTION_HANDLES = 20`
- `semantic_action_family`
- natural language action descriptions in selector input
- renderer text in selector input
- threshold retuning
- RAG baseline weakening
- oracle action-to-effect table
- evaluator metrics in selector input
- baseline outputs in selector input
- rewriting 003 results as if they were parametric
- EGO integration
- real companion implementation
- proactive messages
- LLM action selection

## Allowed Verdicts

- `parametric_action_interface_contract_ready`
- `contract_incomplete`
- `shadow_adapter_invalid`
- `semantic_leak_risk_unresolved`
- `evidence_preservation_failed`
- `baseline_contract_incomplete`
- `renderer_adapter_contract_incomplete`
- `boundary_violation`

## Required Artifacts

- `PARAMETRIC_ACTION_INTERFACE_005_STATUS.md`
- `CMBC_COMPANION_PARAMETRIC_ACTION_INTERFACE_005_CONTRACT.md`
- `candidate_option.schema.json`
- `parametric_selector_input.schema.json`
- `prediction_before_action_per_option.schema.json`
- `action_distribution_over_options.schema.json`
- `parametric_replay_trace.schema.json`
- `shadow_7_action_adapter_contract.md`
- `expanded_baseline_contract.md`
- `renderer_adapter_contract.md`
- `evidence_preservation_contract.md`
- `risk_register_005.md`
- `contract_manifest.json`

## Pass Criteria

- variable-N option list is explicitly supported
- N=7 compatibility path is defined without rewriting 003 evidence
- N>=20 future execution path is defined
- selector-visible fields exclude semantic labels, rendered text, public action names, action family names, natural language descriptions, hidden future state, oracle effects, evaluator metrics, and baseline outputs
- replay can reconstruct from full option distribution
- baselines receive the same anonymous options as selector
- renderer remains strictly post-selection
- no implementation or selector patch occurs

## Recommended Next Task

If ready, the recommended next task is:

`CMBC-COMPANION-PARAMETRIC-ACTION-INTERFACE-005-SHADOW-IMPLEMENT`

That task is not authorized by this contract.
