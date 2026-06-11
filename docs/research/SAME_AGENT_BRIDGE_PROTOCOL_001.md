# SAME_AGENT_BRIDGE_PROTOCOL_001

Task: SAME-AGENT-BRIDGE-GOVERNANCE-001-FIXA
Layer: engineering implementation plus mechanism hypothesis testing.
Mode: governance / protocol / documentation only.

This protocol defines the minimum rules for any future same-agent
Gate0-to-Gate1 bridge attempt. It does not implement an agent, environment,
evaluator, replay system, or baseline.

## Frozen Context

Gate 0 is frozen as `PREDICTIVE-ACTION-LEARNING-CONTRACT-001C`.

Exact Gate 0 claim ceiling:

```text
001C has passed-with-caveats the independent evidence audit for bounded
isolated Gate 0 predictive-action mechanism evidence.
```

Gate 0 does not support functional subject claims, agency claims,
self-awareness claims, emotion claims, companion readiness, or EGO mainline
integration.

## Prior Negative Evidence

This bridge protocol inherits the negative Gate 1 lineage. It must not imply
that Gate 1 is untouched or unexplored.

Prior task:

```text
GATE1-REPLAY-CONSOLIDATION-EXEC-TASKCARD-001
verdict = gate1_preflight_failed_graph_cache_collapse
```

The prior Gate 1 execution failed because the graph-cache family matched or
dominated the tested operationalization. The collapse family included:

- `graph_lookup`
- `transition_table`
- `successor_map`
- `count_table`
- `fsm_planner`
- `episodic_traversal`

Prior residue task:

```text
LATENT-MULTISTEP-CONSISTENCY-RESIDUE-001A
relevant negative pattern = shuffled_same_loss_and_function_approximation_collapse
```

That residue established that shuffled/reverse same-loss replay, generic
training controls, and stronger bounded sequence/window or function
approximation baselines can dominate weak belief/replay claims.

Standing negative evidence:
window, table, graph/cache, and cheap function-approximation models can
dominate weak belief/replay mechanisms when the environment is lookup-trivial,
when transition structure is directly cacheable, or when the claimed mechanism
does not show bridge dependency.

This protocol differs from those failed attempts by requiring a same-agent
bridge dependency, explicit state lineage, frozen decision rules, complete run
ledger, competence-checked baselines, and first-class graph/cache challenger
families before any bridge claim is allowed.

## Binding Terms

Local gate:
A bounded test of one mechanism in isolation. It supports only the local claim
ceiling stated by its task card.

Bridge gate:
A bounded test that requires an earlier gate's trace/state evidence to be used
by a later gate in the same minimal agent, with ablations showing the later
effect weakens or disappears when the earlier trace dependency is removed,
corrupted, or replaced by a baseline memory.

Integrated run:
A single run family in which the same minimal agent instance produces Gate 0
contract traces, carries canonical state forward, performs the later mechanism,
and is evaluated on held-out variants without swapping in a second logic path.

Integration debt:
Any local positive result that has not yet been shown to contribute to a
same-agent bridge. Integration debt must be recorded in the evidence report.
It is not bridge evidence.

Same-agent continuity:
Continuity must be verified through state lineage, schema versioning, replayable
state transition records, and a state hash chain or equivalent. A shared
`agent_id` string alone is insufficient.

Cross-gate ablation:
An ablation that removes, corrupts, replaces, or weakens an earlier gate's
trace/state contribution and measures whether the later gate's claimed effect
depends on that contribution.

Held-out environment transfer:
Evaluation on withheld seeds or generated variants not used for threshold
selection, replay-item selection, salience tuning, or task-card adjustment.

Evidence freeze:
The task card, environment contract, seeds, held-out split, schema, baselines,
ablations, metrics, margins, runtime access manifest, competence checks, and
acceptance rules must be committed or otherwise frozen before first execution.

When EGO integration is forbidden:
Always, unless a prior governance document explicitly authorizes it and a
bounded task card names the exact allowed EGO files. A local or bridge pass
never implies EGO integration readiness.

## Gate 0 Mechanism Provenance

Future bridge implementation must not imply direct continuity from frozen 001C
artifacts to `CausalMemoryGrid-v0` unless it actually establishes that
continuity in implementation and evidence.

Default bridge claim:

```text
re-instantiated Gate 0 contract within the bridge environment
```

Before implementation begins, the task must choose and freeze exactly one of:

- reuse 001C mechanism code inside the new bridge environment
- reimplement the 001C contract inside the new bridge environment
- import frozen 001C artifacts as read-only historical inputs

If this choice is unresolved, implementation is blocked. Importing frozen 001C
artifacts does not by itself establish same-agent continuity in
`CausalMemoryGrid-v0`.

## Environment Contract: CausalMemoryGrid-v0

`CausalMemoryGrid-v0` is the proposed minimal generated environment family for
the bridge. This protocol defines the contract only.

Required properties:

- small enough for exhaustive trace inspection
- seedable
- partially observable
- action-conditioned
- able to generate withheld variants
- able to test whether replay/consolidation improves later behavior
- able to distinguish action-conditioned learning from RAG, nearest-neighbor,
  observation-only memory, random/majority baselines, frequency heuristics,
  and graph/cache family baselines

Because this environment is especially vulnerable to transition-table and
successor-map collapse, the graph/cache baseline family is mandatory and
first-class, not optional diagnostics.

The environment must not leak hidden labels through observation text, filenames,
action names, seed names, fixture names, renderer-visible behavior, or artifact
paths.

## Mandatory Baseline Families

Graph/cache family, first-class challengers:

- `graph_lookup`
- `transition_table`
- `successor_map`
- `count_table`
- `fsm_planner`
- `episodic_traversal`

Other mandatory baselines:

- `random_baseline`
- `majority_baseline`
- `RAG_summary_baseline`
- `nearest_neighbor_trace_baseline`
- `frequency_heuristic_baseline`
- `observation_only_memory_baseline`
- `no_action_conditioning_baseline`
- `same_agent_no_replay_baseline`
- `corrupted_replay_ablation`
- `oracle_leak_scan`

If any graph/cache family baseline matches or beats the mechanism under the
predeclared margin, the bridge verdict must be `fail` or `blocked`, the
appropriate failure taxonomy label must be emitted, and no bridge evidence
claim is allowed.

## Decision Package Freeze

Before implementation begins, the following decision package must be filled,
committed or otherwise frozen, and referenced by hash:

- metrics
- number of training seeds
- number of held-out seeds
- held-out split rule
- baseline equivalence margin
- minimum same-agent held-out delta
- minimum ablation sensitivity margin
- definition of "matches or beats"
- margin-freeze ordering requirement
- baseline competence checks
- control competence checks
- complete `run_ledger.json` schema for completed, failed, and aborted runs

If exact numbers cannot be justified at governance time, they must remain
placeholders marked `implementation_blocking_unresolved`. Implementation must
not begin until they are resolved and frozen. Threshold tuning after seeing
results triggers `threshold_tuning_dependency`.

## Bridge Requirement

Gate 1 replay/consolidation only counts if it demonstrably uses same-agent
Gate 0 action-conditioned prediction-error traces and improves same-agent
held-out behavior.

The claimed bridge must show all of the following:

- Gate 0 contract traces are generated or imported through the frozen
  provenance choice.
- Gate 1 receives canonical Gate 0 trace fields through the frozen trace/replay
  contract.
- Held-out behavior improves against the same-agent no-replay version by the
  frozen minimum delta.
- Required ablations weaken or remove the bridge effect by the frozen
  sensitivity margin.
- First-class challenger baselines do not match or beat the mechanism.
- Same-agent continuity is verified through state lineage and hash-chain or
  equivalent records.

## Required Cross-Gate Ablations

Every bridge task must include:

- remove Gate 0 trace
- remove prediction-error trace
- corrupt replay order
- replace trace with observation-only memory
- replace trace with RAG summary
- compare against same-agent no-replay version

If Gate 1 works without the Gate 0 trace, the bridge dependency is missing.

## Stop Conditions

Stop and report `fail` or `blocked` if any of the following occur:

- any graph/cache family baseline matches or beats the mechanism
- RAG baseline matches or beats the mechanism
- heuristic baseline matches or beats the mechanism
- nearest-neighbor baseline matches or beats the mechanism
- random or majority baseline matches or beats the mechanism
- observation-only memory matches the mechanism
- no-action-conditioning matches the mechanism
- corrupted replay preserves the claimed effect
- replay improves seen seeds only
- no held-out improvement
- trace causality cannot be established
- same-agent continuity cannot be established from state lineage
- Gate 1 works without Gate 0 trace
- schema fragmentation
- threshold tuning dependency
- hidden oracle/leak suspicion
- baseline or control competence check missing
- accidental EGO mainline change

Do not patch around these failures inside the same execution.

## Claim Ceiling

The strongest possible future pass claim is:

```text
bounded same-agent Gate0-to-Gate1 bridge evidence under the specified
trace/replay contract.
```

Explicitly forbidden claims:

- consciousness
- subjective experience
- real emotion
- agency
- stable autonomy
- functional subject success
- companion readiness
- EGO mainline readiness

## Rollback Policy

If any stop condition triggers, rollback must preserve the evidence and state
the failed premise. Allowed rollback outcomes:

- revise task card before execution
- narrow the bridge hypothesis
- improve baseline parity before rerun
- repair schema contract before rerun
- block Gate 1 bridge execution
- keep Gate 0 frozen and make no stronger claim

Rollback must not delete prior artifacts or rewrite failed evidence into a pass.

## What This Protocol Does Not Prove

This protocol does not prove Gate 1 works. It does not prove replay,
consolidation, agency, functional subject success, consciousness, subjective
experience, real emotion, companion readiness, or EGO mainline readiness.
