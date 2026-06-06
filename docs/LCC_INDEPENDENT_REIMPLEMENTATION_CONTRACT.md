# LCC Independent Reimplementation Contract

Contract ID: `LCC_INDEPENDENT_REIMPLEMENTATION_001`

Status: contract package only. Implementation is not authorized by this task.

Package verdict: `independent_reimplementation_contract_ready`

## Goal

Define a clean-room replication protocol where a future independent implementer can test the core LCC evidence using only public materials:

- `docs/LCC_PUBLIC_THEORY_CARD.md`
- `docs/LCC_PUBLIC_IO_SCHEMA.md`
- `docs/LCC_PUBLIC_REDTEAM_GATES.md`
- `docs/LCC_REPLICATION_CLAIM_BOUNDARY.md`
- `artifacts/independent_reimplementation/contract_manifest.json`

The purpose is not to make LCC win. The purpose is to determine whether the Cycle 000-010 evidence survives outside the current code lineage.

## Current Claim Ceiling

Current maximum claim:

LCC_v0 survived eleven bounded contract redteams in one evolving repository, including candidate freeze, blind holdout generation after freeze, independent trace-only scoring, generic baseline proxies, statistical replication, blind-holdout ablations, and negative controls.

This is not LCC theory support and not a bottom intelligence principle.

## Clean-Room Rule

The independent implementer may use public requirements but must not inspect, import, copy, adapt, or tune against current internals:

- Current candidate/control code.
- Cycle-specific runner internals.
- Expected-output tables.
- Current scorer internals.
- Hidden transition tables.
- Oracle plan tables.
- Semantic action labels.
- Evaluator metric features.
- Hidden future state.
- Task IDs, goal IDs, cycle IDs, contract IDs, scenario IDs, object names, or entity names as candidate inputs.

## Minimum Replication Suite

The independent suite should not reproduce all Cycle 000-010 tasks first. It must start with five core gates:

1. Label/effect decoupling.
2. Passive observation versus own intervention.
3. Active diagnostic intervention.
4. Sequential closed-loop replanning.
5. Blind holdout after candidate freeze.

If these fail, do not expand the suite. Record the failure and downgrade the claim.

## Required Baselines

The independent implementation must include at least:

- `ActionLabelHeuristic`
- `NearestNeighborTracePolicy`
- `ContextualHeuristic`
- `ModelBasedMPCBaseline`
- `EmpowermentProxyBaseline`
- `OracleDiagnosticUpperBound` as diagnostic only, not a valid competitor

The model-based and empowerment baselines are mandatory because Milestone 001 identified collapse risk into model-based causal control, active inference, or empowerment-style control.

## Required Gates

The candidate must pass:

- Hidden-state leak scan.
- Evaluator-metric leak scan.
- Action-label use scan.
- Behavior-only replay.
- Label-permutation invariance.
- Effect-swap sensitivity.
- Passive-correlation rejection.
- Diagnostic intervention selection under uncertainty.
- Closed-loop replanning after unexpected observations.
- Strong baseline non-equivalence.
- Candidate freeze before blind holdout generation.
- No candidate/control code changes after blind holdout generation.

## Stop Conditions

Stop and record failure if:

- Label permutation changes behavior while effects stay fixed.
- Effect swap does not change behavior while labels stay fixed.
- Passive correlation is treated as own-intervention effect.
- Effect model perturbation does not alter action distribution.
- Behavior-only replay cannot reconstruct decision evidence.
- A strong non-oracle baseline matches the candidate within the declared equivalence band.
- Candidate reads semantic labels, evaluator metrics, hidden state, hidden future state, oracle plans, or expected outputs.
- Candidate/control code changes after blind holdout generation.

## Allowed Future Run Verdicts

- `independent_reimplementation_bounded_pass`
- `label_shortcut_detected`
- `intervention_effect_not_learned`
- `diagnostic_intervention_failed`
- `closed_loop_replanning_failed`
- `behavior_only_replay_failed`
- `hidden_or_metric_leak_detected`
- `strong_baseline_equivalent`
- `freeze_integrity_violation`
- `inconclusive_contract_needs_revision`

## Package Verdicts

This package may only conclude one of:

- `independent_reimplementation_contract_ready`
- `contract_not_ready_due_to_underspecified_mechanism`
- `contract_not_ready_due_to_baseline_gap`
- `contract_not_ready_due_to_claim_ambiguity`
- `contract_not_ready_due_to_lineage_dependency`

This package concludes `independent_reimplementation_contract_ready`.

## Failure Consequence

If independent reimplementation fails, the current implementation must not be patched to recover the claim. The correct consequence is downgrade to bounded single-lineage evidence unless a later human review explicitly authorizes a revised public contract.
