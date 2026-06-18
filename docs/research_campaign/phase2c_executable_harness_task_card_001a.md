# Phase2C Executable Harness Task Card 001A

Task id: `RESEARCH-CAMPAIGN-PHASE2C-EXECUTABLE-HARNESS-TASK-CARD-001A`

Status: focused validation passed; read-only reviewer audit pending.

Source contract:
`docs/research/phase2c_hidden_latent_heldout_surface_contract_001a.md`

Source checkpoint:
`RESEARCH-CAMPAIGN-PHASE2C-HIDDEN-LATENT-HELDOUT-SURFACE-CONTRACT-001A`

## Purpose

Open a bounded task card for a future candidate-free Phase2C executable harness.
This card does not implement or execute that harness.

The future harness must test whether a small generated surface has measured
headroom after two prior visible-surface failures:

- Phase 2: `count_table` matched the visible-channel oracle at macro F1 `1.0`.
- Phase2B: `count_table` again matched the visible-channel oracle at macro F1
  `1.0`.

The next executable work must therefore prove the surface is not solved by
visible lookup, count table, transition table, graph-cache, nearest-neighbor,
episodic traversal, or exhaustive legal-query routes before any mechanism
candidate or Phase 3 search is opened.

## Current Layer

`engineering_implementation + mechanism_hypothesis_governance`

This is a task-card-opening checkpoint for a future candidate-free harness. It
is not mechanism execution, not a candidate run, not subjectivity validation,
and not philosophical consciousness work.

## Bounded Audit Before Execution

Real objective: define the future executable harness scope tightly enough that
the first executable run can decide whether the Phase2C hidden-latent heldout
surface has baseline headroom before candidate work.

Problem-definition risk: the campaign may repeat the Phase 2 / Phase2B error by
building a larger surface whose visible fields still encode enough regularity
for cheap baselines to match the oracle.

Strongest baseline explanation: a non-learning route using visible observations,
legal action order, trace order, seed or family identity, count tables,
transition tables, graph cache, nearest-neighbor retrieval, or exhaustive legal
queries could match oracle behavior without latent inference, exploration, or
memory.

Strongest invalidating reason: if hidden latent state, heldout task-family
transfer, exploration evidence, and memory/intervention effects are not
independently callable and replayable, the harness will produce only behavioral
resemblance or static bookkeeping.

Falsifier for the current framing: if the future no-candidate harness reports
the strongest fair baseline within the oracle equivalence band on heldout latent
rules or heldout task families, candidate mechanisms and Phase 3 remain blocked
and the surface must be redesigned or closed.

Evidence that would still be insufficient:

- a candidate score without candidate-free baseline headroom;
- a hidden state recorded only in artifact metadata;
- heldout seeds without heldout latent-rule or task-family splits;
- replay that compares stored hashes instead of recomputing behavior;
- ablations that flip stored labels instead of rerunning episodes;
- leakage scans without positive controls;
- a scalar score without failure taxonomy.

Mechanism-vs-behavior classification: this future harness can test whether a
surface is suitable for later mechanism testing. It cannot validate a mechanism
by itself.

Hard-coding, leakage, and weak-baseline checks:

- hidden rule, oracle action, split identity, seed identity, target label,
  answer map, legal action rank, and final score must be absent from
  candidate-visible observations and baseline-visible fields;
- baseline input boundaries must be explicit and at least as fair as candidate
  input boundaries;
- positive controls must prove the leakage scanner catches injected leaks;
- any unused frozen seed, train context, heldout context, counterfactual pair,
  intervention, or baseline blocks the evidence claim.

## Collision Record

### Candidate A: Minimal visible harness

Evidence it would produce: quick candidate-free generator/oracle/baseline
execution over a small surface.

Strongest cheap baseline that could match it: count table, lookup, transition
table, graph-cache, nearest-neighbor, or exhaustive legal query.

Leakage / hard-coding risk: high, because a minimal visible task can again put
oracle-relevant structure in current observation, legal action set, or task
family identity.

Smallest falsifying test: run the required baseline battery on heldout latent
rules; if any baseline reaches the oracle equivalence band, stop.

Expected failure mode: repeats Phase 2 / Phase2B no-headroom.

Decision: rejected as the primary route.

### Candidate B: Strongest shortcut-baseline harness

Evidence it would produce: direct negative-control pressure by implementing the
strongest non-learning routes first and trying to solve the surface.

Strongest cheap baseline that could match it: this candidate is the cheap
baseline family itself.

Leakage / hard-coding risk: medium. It is useful as a negative-control probe,
but if treated as the whole harness it cannot test exploration, memory,
intervention sensitivity, or replay beyond shortcut closure.

Smallest falsifying test: any baseline finds a visible, trace-order, identity,
or exhaustive-query route to oracle-equivalent heldout behavior.

Expected failure mode: proves no headroom but does not leave enough executable
scaffolding to inspect why the surface failed.

Decision: required as a first-class baseline component, not sufficient as the
full harness.

### Candidate C: Mechanism-faithful hidden-latent heldout harness

Evidence it would produce: candidate-free environment generation, oracle,
baseline comparison, interventions, replay recomputation, leakage positive
controls, and failure taxonomy over hidden latent rules and heldout task
families.

Strongest cheap baseline that could match it: observation-only, lookup,
count-table, transition-table, graph-cache, successor-map, nearest-neighbor,
FSM planner, episodic traversal, trace-only replay, and exhaustive legal query.

Leakage / hard-coding risk: high if hidden variables leak through identifiers,
action names, legal order, or trace fields; acceptable only with positive
controls and field-access audits.

Smallest falsifying test: baseline equivalence on heldout latent rules,
heldout task families, memory deletion, latent-rule swap, or exploration-budget
ablation.

Expected failure mode: the surface still collapses to a shortcut baseline, or
interventions fail to change behavior when they should.

Decision: selected as the future executable harness route.

## Reference Design Mapping

The references below are design analogies only. They are not imported proof.

- Procgen motivates frozen train/heldout procedural splits and separate
  generalization measurement: https://arxiv.org/abs/1912.01588
- MiniGrid/MiniWorld motivates small, controllable, rapidly customizable
  environments before expensive worlds: https://openreview.net/forum?id=PFfmfspm28
- DeepMind Alchemy motivates procedurally resampled latent causal structure,
  online inference, hypothesis testing, and action sequencing:
  https://openreview.net/forum?id=eZu4BZxlRnX
- POPGym motivates partial observability, memory baselines, and low-compute
  memory-sensitive benchmark design: https://arxiv.org/abs/2303.01859
- Meta-World motivates heldout task-family transfer rather than narrow task
  distributions: https://arxiv.org/abs/1910.10897
- Continual World motivates forward transfer, forgetting, capacity, and compute
  constraints: https://arxiv.org/abs/2105.10919
- AgentBench motivates multi-turn interactive failure categorization:
  https://arxiv.org/abs/2308.03688
- Craftax motivates complexity only when it buys exploration, long-horizon
  planning, memory, or continual adaptation under feasible compute:
  https://arxiv.org/abs/2402.16801

## Problem Definition

The future task must implement a candidate-free executable harness for the
Phase2C hidden-latent heldout surface. The harness must answer:

```text
Does this surface have measured baseline headroom on heldout latent structure
under fair, callable, no-candidate baselines?
```

It must not answer:

```text
Can a mechanism candidate beat a baseline?
```

Candidate mechanisms, Phase 3, route tournament, runtime/EGO mainline, UI, LLM,
AIRI, external services, deployment, push, tag, remote anchor, and terminal
verdicts remain unauthorized.

## Mainline Target

None. The future harness is an isolated offline candidate-free evaluation path
only.

## Enabled-State Requirement

This task-card checkpoint enables only:

- this task card;
- a focused validation artifact for this task-card checkpoint;
- plan/progress/scorecard/ledger bookkeeping.

After focused validation and read-only reviewer audit both succeed, a later
bounded task may implement the future candidate-free harness under isolated
paths only:

- `src/phase2c_hidden_latent_heldout_harness_001a/`
- `tests/phase2c_hidden_latent_heldout_harness_001a/`
- `artifacts/phase2c_hidden_latent_heldout_harness_001a/`
- `artifacts/research_campaign/phase2c_hidden_latent_heldout_harness_001a.json`
- `artifacts/research_campaign/phase2c_hidden_latent_heldout_harness_validation_001a.json`
- `artifacts/research_campaign/phase2c_hidden_latent_heldout_harness_audit_001a.json`

No harness implementation or execution is enabled by this card-opening
checkpoint alone.

## Real-Trigger Evidence Requirement

This checkpoint must read and record:

- repo root, branch, HEAD, upstream/ahead-behind, and
  `git status --short --branch -uall`;
- `docs/research_campaign/goal_stage_audit_loop_001a.md`;
- `docs/research_campaign/plan.md`;
- `docs/OVERALL_PROGRESS.md`;
- `artifacts/research_campaign/stage_scorecard.json`;
- `artifacts/research_campaign/experiment_log.jsonl`;
- `docs/research_campaign/phase2c_hidden_latent_heldout_surface_contract_task_card_001a.md`;
- `docs/research/phase2c_hidden_latent_heldout_surface_contract_001a.md`;
- `artifacts/research_campaign/phase2c_hidden_latent_heldout_surface_contract_001a.json`;
- `artifacts/research_campaign/phase2c_hidden_latent_heldout_surface_contract_validation_001a.json`;
- `artifacts/research_campaign/phase2c_hidden_latent_heldout_surface_contract_audit_001a.json`;
- `artifacts/research_campaign/phase2_no_headroom_negative_evidence_001a.json`;
- `artifacts/research_campaign/phase2b_no_headroom_negative_evidence_001a.json`;
- primary-source reference URLs listed in this card.

## Hypothesis

A small candidate-free executable harness with hidden latent rules, heldout
task-family transfer, online exploration probes, bounded memory, intervention
hooks, strict leakage controls, replay recomputation, and a full shortcut
baseline battery can decide whether the Phase2C surface has enough headroom for
later mechanism testing.

## Strongest Baseline

The future harness must implement and invoke at least:

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

The surface fails if the strongest fair baseline reaches the oracle equivalence
band on heldout latent rules or heldout task families.

## Ablation Requirement

The future harness must rerun episodes, not mutate stored scores, for:

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
+ budget_state + latent-belief_or_memory_state
```

Stored action labels, stored verdicts, stored hashes, and report equality are
not replay evidence.

## Computed-Evidence Provenance Gate

The future executable harness must record callable producers for:

- environment generation;
- train/heldout seed and task-family split generation;
- oracle policy;
- every baseline;
- every intervention;
- leakage scan and positive controls;
- replay recomputation;
- failure taxonomy assignment;
- final aggregation.

Every score must record producer function, input artifacts, run id,
seed/context/episode ids, aggregation rule, and code path hash.

## Future Harness Required Artifacts

Unless a later implementation task card narrows this list, the future harness
must write:

- `artifacts/phase2c_hidden_latent_heldout_harness_001a/result.json`;
- `artifacts/phase2c_hidden_latent_heldout_harness_001a/trace.jsonl`;
- `artifacts/phase2c_hidden_latent_heldout_harness_001a/baseline_comparison.json`;
- `artifacts/phase2c_hidden_latent_heldout_harness_001a/ablation_report.json`;
- `artifacts/phase2c_hidden_latent_heldout_harness_001a/replay_report.json`;
- `artifacts/phase2c_hidden_latent_heldout_harness_001a/leakage_report.json`;
- `artifacts/phase2c_hidden_latent_heldout_harness_001a/computed_evidence_provenance.json`;
- `artifacts/phase2c_hidden_latent_heldout_harness_001a/failure_manifest.json`;
- `artifacts/phase2c_hidden_latent_heldout_harness_001a/claim_ceiling.txt`.

## Acceptance Gate

This task-card-opening checkpoint is accepted only if:

- this task card exists and contains the required bounded-task fields;
- collision record is present and selects the mechanism-faithful harness route;
- prior Phase 2 and Phase2B no-headroom evidence is cited as a blocker against
  visible-surface repetition;
- reference mappings are recorded as analogies with failure boundaries;
- source implementation and tests remain untouched;
- candidate mechanisms remain unrun;
- Phase 3 remains unopened;
- route tournament remains unauthorized;
- harness implementation and execution remain unauthorized until a later
  focused validation and read-only reviewer audit succeed;
- plan/progress/scorecard/ledger agree on this checkpoint and next frontier;
- focused validation passes.

## Claim Ceiling

This checkpoint can claim only a bounded executable-harness task card has been
opened for future candidate-free Phase2C baseline-headroom evaluation.

It does not prove mechanism validity, learning/adaptation success, selfhood,
subjective experience, real emotion, autonomy, EGO readiness, companion
readiness, runtime readiness, user benefit, route exhaustion, program
completion, or mainline effect.

## Stop Conditions

Stop and record a blocker if:

- the task card authorizes candidate mechanisms, Phase 3, route tournament,
  runtime/EGO mainline, UI, LLM, AIRI, external services, deployment, push, tag,
  remote anchor, terminal verdict, or program completion;
- the task card omits strong shortcut baselines;
- the task card treats bigger task size as a substitute for hidden latent
  inference, heldout transfer, exploration, or memory;
- future replay, ablation, leakage, or provenance requirements are static or
  self-reported;
- prior Phase 2 / Phase2B no-headroom evidence is omitted;
- source, tests, or harness artifacts are modified during this card-opening
  checkpoint;
- plan/progress/scorecard/ledger disagree after repair.

## Rollback Plan

Rollback this checkpoint only by reverting:

- `docs/research_campaign/phase2c_executable_harness_task_card_001a.md`;
- `artifacts/research_campaign/phase2c_executable_harness_task_card_validation_001a.json`;
- matching plan/progress/scorecard/ledger updates.

Do not delete or rewrite prior Phase 2, Phase2B, Phase2C contract, failed
validation, failed audit, no-headroom, or route-decision evidence.

## Expected Changed Files

- `docs/research_campaign/phase2c_executable_harness_task_card_001a.md`
- `artifacts/research_campaign/phase2c_executable_harness_task_card_validation_001a.json`
- `docs/research_campaign/plan.md`
- `docs/OVERALL_PROGRESS.md`
- `artifacts/research_campaign/stage_scorecard.json`
- `artifacts/research_campaign/experiment_log.jsonl`

## Forbidden Changes

- No source implementation changes.
- No test changes.
- No harness implementation.
- No harness execution.
- No candidate mechanism implementation.
- No candidate score.
- No Phase 3 mechanism search.
- No route tournament.
- No formal Gate execution.
- No runtime, EGO mainline, UI, LLM, AIRI, external service, deployment, push,
  tag, or remote anchor.
- No mutation, normalization, amendment, or refreeze of prior specs.
- No rewriting prior failed artifacts into passes.
- No terminal verdict or program-completion claim.

## Local Commit

Local commit is authorized only for this durable task-card-opening checkpoint
after focused validation, exact-path staging, staged-set verification, and
final dirty-path classification. `git add -A` remains forbidden.

## Auto-Remote-Anchor

`forbidden`

## Immediate Next Action After This Card

Run focused validation for this task-card-opening checkpoint, then run
read-only reviewer audit before any harness implementation or execution.
