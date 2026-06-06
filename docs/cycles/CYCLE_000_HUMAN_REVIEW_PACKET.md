# Cycle 000 Human Review Packet

## Decision Required

Cycle 000 has opened a proposed candidate, `LCC_v0`, and a contract-only experiment, `LCC_EFFECT_SWAP_001`.

The reviewer must choose exactly one next status:

```text
authorize_contract_only
revise_contract
reject_candidate
close_current_line
```

`authorize_contract_only` means only the experiment contract is authorized for the next bounded implementation pass. It does not authorize EGO migration, robust theory claims, autonomous theory search, or any general-purpose agent.

## Current Thinking Best Move

Do not keep repairing VCCO, VCAC-Core, or FOPC. Treat them as frozen negative evidence and test a smaller successor framing where learned causal effects, not action labels or trace variables, drive action selection.

## Better Framing Outside Current Thinking

The lab is not a theory generator that should keep producing names. It is a theory elimination machine. A successor is worthwhile only if it introduces a stronger falsifier than the failed lineage.

## Candidate

```text
LCC_v0 = Learned Counterfactual Controllability
```

One-sentence claim:

```text
Intelligence-relevant control requires learned effect-conditioned action selection that follows observed causal effects, not action labels, trace annotations, score-only changes, or evaluator features.
```

## Why This Candidate Exists

The previous lineage failed because recorded variables and scores were too easy to confuse with real control-loop causality:

```text
plastic_selection / repertoire_expansion were no-op components
boundary / action_closure were trace-visible but not causal in the selector
viability / compression were score-sensitive but weak in action-distribution causality
future_action_variety_proxy was action-causal but reducible to action labels
```

LCC_v0 is only worth considering if it breaks the action-label shortcut.

## Minimum Validation Action

Before any performance test, the first future testbed must support:

```text
label permutation: labels change, effects stay fixed
effect swap: labels stay fixed, effects change
```

Expected split:

```text
label permutation should not change behavior
effect swap should change behavior
```

If this split fails, close LCC_v0.

## Stop-Loss / Rollback

Stop immediately if a future implementation tries to:

```text
use semantic action labels
read evaluator metrics
read hidden future state
win only through a static action-safety table
claim score sensitivity as action causality
promote trace-only variables to control-loop components
reintroduce plastic_selection or repertoire_expansion as core
```

Rollback path:

```text
reject LCC_v0
preserve artifacts as negative evidence
return to theory search protocol before naming a successor
```

## Acceptance Signals

For a future implementation pass, not this documentation pass:

```text
label permutation invariant behavior
effect swap sensitive behavior
hidden-state and metric-provenance scans clean
strong heuristic and static-label baselines fail to match
behavior-only replay reconstructs prediction-before-action
ablation semantics audit proves non-no-op components
```

## What This Cannot Prove

This cannot prove:

```text
intelligence principle
consciousness
subjective experience
AGI
self-awareness
life
EGO readiness
robust universal mechanism support
```

At most, a later authorized implementation could support a bounded toy mechanism candidate.

