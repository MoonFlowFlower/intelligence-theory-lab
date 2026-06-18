# Phase2C Hidden-Latent Heldout Surface Contract Task Card 001A

Task id: `RESEARCH-CAMPAIGN-PHASE2C-HIDDEN-LATENT-HELDOUT-SURFACE-CONTRACT-001A`

Source route-decision checkpoint:
`artifacts/research_campaign/phase2b_no_headroom_route_decision_001a.json`

Superseded interrupted checkpoint:
`docs/research_campaign/phase2b_program_needs_reframing_checkpoint_001a.md`

## Purpose

Open a bounded problem-representation redesign checkpoint after the user
corrected the route: the next experiment design must learn how to make visible
surface baselines insufficient, not merely make the task larger.

This card authorizes only a local contract/specification surface for the next
candidate-free environment family. The contract must encode a cheap,
interpretable surface in which oracle behavior depends on hidden latent state,
cross-episode variables, train/heldout splits, and interventions that test
learning, exploration, memory, transfer, and failure taxonomy.

It does not authorize a harness implementation, candidate mechanism, Phase 3,
route tournament, runtime/EGO mainline, UI, LLM, AIRI, external service,
deployment, commit, push, tag, or remote anchor.

## Current Layer

`engineering_implementation + mechanism_hypothesis_governance`

This is problem-representation governance. It is not a mechanism experiment,
not subjectivity validation, and not philosophical consciousness work.

## Bounded Audit Before Execution

Real objective: define a next-surface contract whose success condition is not
"candidate beats baseline" but "the surface requires learning, exploration, or
memory to reproduce oracle behavior on heldout latent structure."

Problem-definition risk: after no-headroom evidence, the campaign may either
quit too early or create a larger task with the same visible-surface leak.

Strongest baseline explanation: `count_table`, lookup, graph-cache,
transition-table, nearest-neighbor, successor-map, FSM planner, episodic
traversal, observation-only decoding, and exhaustive legal query can solve the
previous surfaces because visible observations contain stable answer-like
regularities.

Strongest invalidating reason: a new surface is invalid if current observation,
filename, action label, episode id, legal action order, or static task family
identity lets a non-learning baseline match oracle behavior on heldout cases.

Falsifier for the proposed framing: if a non-learning baseline can match the
visible-channel oracle on heldout latent rules, heldout task families, or after
memory deletion / latent-rule intervention, the surface still does not test the
intended mechanism variables.

Evidence that would still be insufficient:

- bigger state/action space without hidden latent variables;
- fixed train/test seeds without heldout latent structure;
- an online-inference story without memory deletion or latent-rule swap
  interventions;
- a pass/fail score without failure taxonomy;
- a candidate improvement that is not compared to lookup/graph-cache/count
  and transition-table families.

Mechanism-vs-behavior classification: this card defines a mechanism-testing
surface contract. It does not run the mechanism test.

Hard-coding / leakage / weak-baseline checks:

- no candidate mechanism;
- no Phase 3 search;
- no route tournament;
- no harness execution;
- no hidden rule in visible observation, labels, action names, filenames,
  seed ids, or legal action ordering;
- no use of task size as a substitute for latent causal inference;
- no removal of strong baselines;
- no terminal verdict or program-completion claim.

## Problem Definition

Two candidate-free surfaces saturated against `count_table`. The next design
must therefore change the problem representation, not the candidate.

The new contract must ask:

```text
Does this surface require learning, exploration, or memory to get oracle
behavior on heldout latent structure?
```

It must not ask first:

```text
Can a candidate beat the current baseline on the same visible surface?
```

## Mainline Target

None. This card has no runtime, EGO mainline, UI, LLM, AIRI, external service,
deployment, product, or companion target.

## Enabled-State Requirement

Only local docs/artifacts and campaign bookkeeping are enabled:

- create `docs/research/phase2c_hidden_latent_heldout_surface_contract_001a.md`;
- create a campaign result artifact for this contract;
- create a validation artifact;
- update `docs/research_campaign/plan.md`;
- update `docs/OVERALL_PROGRESS.md`;
- update `artifacts/research_campaign/stage_scorecard.json`;
- update `artifacts/research_campaign/goal_stage_audit_loop_validation_001a.json`;
- append to `artifacts/research_campaign/experiment_log.jsonl`;
- update the standing controller card to preserve the principle.

No source implementation, tests, harness execution, candidate, Phase 3, route
tournament, runtime/EGO mainline, push, tag, commit, or remote anchor is
enabled.

## Real-Trigger Evidence Requirement

Execution must read and record:

- repo root, branch, HEAD, upstream/ahead-behind, and
  `git status --short --branch`;
- this task card;
- `docs/research_campaign/goal_stage_audit_loop_001a.md`;
- `docs/research_campaign/plan.md`;
- `docs/OVERALL_PROGRESS.md`;
- `artifacts/research_campaign/stage_scorecard.json`;
- `artifacts/research_campaign/experiment_log.jsonl`;
- `artifacts/research_campaign/phase2_no_headroom_negative_evidence_001a.json`;
- `artifacts/research_campaign/phase2b_no_headroom_negative_evidence_001a.json`;
- `artifacts/research_campaign/phase2b_no_headroom_route_decision_001a.json`;
- the user design correction in this session;
- benchmark references used as design analogies, with explicit mapping and
  failure boundaries.

## Hypothesis

A small, interpretable, procedurally generated surface with hidden latent
causal rules, train/heldout seeds, heldout task families, memory deletion,
latent-rule intervention, and explicit failure taxonomy will better test the
claim-critical variables than another larger visible-surface benchmark.

## Strongest Baseline

The contract must preserve these baselines for future executable work:

- random / majority;
- observation-only;
- lookup;
- count table;
- transition table;
- graph-cache;
- successor map;
- nearest neighbor;
- FSM planner;
- episodic traversal;
- trace-only replay;
- exhaustive legal query.

The surface is invalid if these baselines can match oracle behavior on heldout
latent rules or heldout task families under the same budget.

## Ablation Requirement

This contract does not execute ablations, but future executable work must
predeclare and run:

- memory deletion;
- latent-rule swap;
- heldout task-family transfer;
- partial-observation ablation;
- exploration-budget ablation;
- cross-episode state reset;
- spurious-token injection/removal;
- source-memory deletion or equivalent lineage test.

## Trace / Replay Requirement

Future replay must recompute behavior from:

```text
serialized_state + current_observation + legal_action_or_query_schema
+ budget_state + latent-belief/memory state
```

Hash equality and stored report agreement remain insufficient.

## Computed-Evidence Provenance Gate

This docs-only contract artifact must record:

- producer command or structured readback source;
- source artifacts and hashes;
- benchmark analogy mapping and failure boundary;
- required train/heldout seed policy;
- required latent-rule and intervention policy;
- required baseline battery;
- required failure taxonomy;
- explicit claim ceiling.

Future executable work must record callable producers for generation, oracle,
baseline scoring, interventions, replay recomputation, leakage scans, and
failure taxonomy.

## Acceptance Gate

This checkpoint is accepted only if:

- this task card exists and is the active checkpoint;
- the surface contract exists under `docs/research/`;
- the contract contains the hidden-latent, heldout, intervention, baseline,
  failure-taxonomy, and claim-ceiling requirements;
- the interrupted `program_needs_reframing` checkpoint is marked superseded,
  not treated as terminal evidence;
- plan/progress/scorecard/goal-validation/ledger agree on the active
  Phase2C contract state;
- candidate mechanism, Phase 3, route tournament, runtime/EGO mainline, push,
  tag, commit, and remote anchor remain false/blocked;
- focused validation passes;
- read-only reviewer audit returns `success_reached`, or any failure is
  preserved and repaired without widening scope.

## Claim Ceiling

This checkpoint can claim only a bounded problem-representation contract for a
future candidate-free hidden-latent heldout surface.

It does not prove mechanism validity, learning/adaptation success, selfhood,
subjective experience, real emotion, autonomy, EGO readiness, companion
readiness, runtime readiness, user benefit, route exhaustion, or mainline
effect.

## Stop Conditions

Stop and record a blocker if:

- the contract relies on task size instead of latent inference / heldout
  transfer / intervention;
- any visible field leaks hidden rule, oracle action, seed identity, heldout
  identity, answer map, or final score;
- strong baselines are removed or weakened;
- candidate, Phase 3, route tournament, harness execution, runtime/EGO
  mainline, UI, LLM, AIRI, external service, deployment, commit, push, tag, or
  remote anchor is attempted;
- terminal verdict or program completion is claimed;
- plan/progress/scorecard/ledger disagree after repair.

## Rollback Plan

Rollback this checkpoint only by reverting:

- `docs/research_campaign/phase2c_hidden_latent_heldout_surface_contract_task_card_001a.md`;
- `docs/research/phase2c_hidden_latent_heldout_surface_contract_001a.md`;
- `artifacts/research_campaign/phase2c_hidden_latent_heldout_surface_contract_001a.json`;
- `artifacts/research_campaign/phase2c_hidden_latent_heldout_surface_contract_validation_001a.json`;
- `artifacts/research_campaign/phase2c_hidden_latent_heldout_surface_contract_audit_001a.json`;
- the matching plan/progress/scorecard/goal-validation/ledger/controller-card
  updates.

Do not delete or rewrite prior no-headroom, repair, audit, or route-decision
evidence.

## Expected Changed Files

- `docs/research_campaign/phase2c_hidden_latent_heldout_surface_contract_task_card_001a.md`
- `docs/research/phase2c_hidden_latent_heldout_surface_contract_001a.md`
- `docs/research_campaign/goal_stage_audit_loop_001a.md`
- `artifacts/research_campaign/phase2c_hidden_latent_heldout_surface_contract_001a.json`
- `artifacts/research_campaign/phase2c_hidden_latent_heldout_surface_contract_validation_001a.json`
- `artifacts/research_campaign/phase2c_hidden_latent_heldout_surface_contract_audit_001a.json`
- `docs/research_campaign/plan.md`
- `docs/OVERALL_PROGRESS.md`
- `artifacts/research_campaign/stage_scorecard.json`
- `artifacts/research_campaign/goal_stage_audit_loop_validation_001a.json`
- `artifacts/research_campaign/experiment_log.jsonl`

## Forbidden Changes

- No source implementation changes.
- No test changes.
- No candidate mechanism implementation.
- No Phase 3 mechanism search.
- No route tournament.
- No new harness execution.
- No formal Gate execution.
- No runtime, EGO mainline, UI, LLM, AIRI, external service, deployment,
  commit, push, tag, or remote anchor.
- No mutation, normalization, amendment, or refreeze of prior specs.
- No rewriting prior failed artifacts into passes.
- No terminal verdict or program-completion claim.

## Auto-Remote-Anchor

`forbidden`

## Immediate Next Action After This Card

Write the hidden-latent heldout surface contract, validate it locally, and run
read-only reviewer audit. Candidates, Phase 3, route tournament, runtime/EGO
mainline, push, tag, commit, and remote anchor remain blocked.
