# Phase2C Hidden-Latent Heldout Surface Contract 001A

Task id: `RESEARCH-CAMPAIGN-PHASE2C-HIDDEN-LATENT-HELDOUT-SURFACE-CONTRACT-001A`

Status: draft contract pending validation and reviewer audit.

## Contract Purpose

Phase2C must learn from the Phase 2 and Phase2B no-headroom results:

```text
The next surface must make visible-surface baselines insufficient.
It must not merely make the task larger.
```

The first question is:

```text
Does the surface require learning, exploration, or memory to reproduce oracle
behavior on heldout latent structure?
```

The first question is not:

```text
Can a candidate beat the baseline on another visible-surface task?
```

## Design Principles From Reference Benchmarks

The references are design analogies, not imported proof.

### Procgen Mapping

Useful principle: procedural generation must include train/test splits and
heldout surfaces.

Phase2C requirement:

- freeze train seed ranges and heldout seed ranges before execution;
- report train and heldout scores separately;
- reject any surface where fixed train cases predict heldout oracle behavior
  through lookup, count table, graph-cache, or successor-map reuse.

Failure boundary:

- procedural variety is insufficient if the latent rule and oracle action are
  still visible from current observation.

### MiniGrid / MiniWorld Mapping

Useful principle: use small, controllable, interpretable environments first.

Phase2C requirement:

- keep the environment cheap enough for exhaustive baseline batteries and
  positive-control leakage scans;
- expose partial observations;
- keep hidden variables auditable by trace after the episode, not visible to the
  agent during action selection.

Failure boundary:

- do not use a large world to hide weak experimental design.

### DeepMind Alchemy Mapping

Useful principle: latent causal structure should be resampled and inferred
through exploration, hypothesis testing, and action sequencing.

Phase2C requirement:

- include latent rule families that change across episodes or task families;
- require exploratory actions to identify the active latent rule;
- score post-identification behavior separately from pre-identification
  exploration;
- include latent-rule swap interventions.

Failure boundary:

- if oracle behavior can be recovered without latent belief updates, the surface
  is not testing learning/inference.

### Meta-World Mapping

Useful principle: heldout new tasks test transfer better than one repeated
task.

Phase2C requirement:

- include train task families and heldout task families;
- score heldout adaptation after limited evidence;
- separate within-family generalization from new-family transfer.

Failure boundary:

- solving one task family, or one heldout seed with the same rule, is not
  mechanism evidence.

### Continual World Mapping

Useful principle: long-lived agents must balance forward transfer, forgetting,
capacity, and compute.

Phase2C requirement:

- include a task sequence mode;
- measure forward transfer and forgetting;
- enforce a bounded memory/capacity budget;
- include cross-episode memory reset and source-memory deletion interventions.

Failure boundary:

- a score that ignores forgetting or capacity is not evidence of durable
  learning/update.

### AgentBench Mapping

Useful principle: multi-round interactive failure taxonomy is part of the
evidence, not a prose afterthought.

Phase2C requirement:

- every failed episode must classify failure into a machine-readable taxonomy;
- taxonomy must include exploration failure, latent-rule inference failure,
  memory-update failure, transfer failure, baseline-equivalence failure,
  leakage failure, and instruction/schema failure;
- score summaries must include failure-family counts.

Failure boundary:

- a scalar score without failure taxonomy is insufficient.

### Craftax Mapping

Useful principle: complexity should buy exploration, long-term planning,
memory, and continual adaptation under feasible compute.

Phase2C requirement:

- add complexity only when it supports hidden-state inference, delayed
  consequences, memory, or adaptation;
- keep compute low enough to run strong baselines and interventions;
- measure exploration-depth and planning-horizon separately.

Failure boundary:

- more rules, bigger maps, or longer episodes are invalid if they do not
  change the baseline-equivalence risk.

## Required Surface Properties

The future Phase2C executable surface must include all of these:

1. Hidden latent rule or state.
2. Current observation cannot directly imply the oracle action.
3. Cross-episode variable or memory-relevant state.
4. Frozen train seeds and heldout seeds.
5. Heldout task-family split, not only heldout instances.
6. Online exploration actions that reveal partial evidence about the latent
   rule.
7. Bounded memory/capacity budget.
8. Intervention hooks for memory deletion and latent-rule swap.
9. Machine-readable failure taxonomy.
10. Positive-control leakage cases.

## Forbidden Surface Leaks

The future surface must not expose hidden answers through:

- observation tokens;
- filenames;
- seed ids;
- heldout ids;
- task-family names visible to the agent;
- action names;
- legal action ordering;
- final-action scores;
- answer maps;
- full legal response bundles;
- serialized hidden state;
- trace-only replay labels;
- renderer-visible behavior used as causal evidence.

## Required Baseline Battery

Future executable work must retain these baselines:

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

The surface fails the contract if the strongest fair baseline reaches the
visible-channel oracle within the equivalence band on heldout latent rules or
heldout task families.

## Required Interventions

Future executable work must include:

- memory deletion;
- latent-rule swap;
- heldout task-family transfer;
- partial-observation ablation;
- exploration-budget ablation;
- cross-episode state reset;
- spurious-token injection/removal;
- source-memory deletion or equivalent lineage test.

Each intervention must rerun episodes through the same callable producer path.

## Required Metrics

The future harness must report at least:

- train score;
- heldout seed score;
- heldout task-family score;
- sample efficiency curve;
- post-identification score;
- exploration efficiency;
- memory deletion delta;
- latent-rule swap sensitivity;
- forward transfer;
- forgetting;
- strongest fair baseline score;
- baseline gap on heldout latent rules;
- failure taxonomy counts.

## Required Trace / Replay Contract

Replay must recompute behavior from:

```text
serialized_state + current_observation + legal_action_or_query_schema
+ budget_state + latent-belief/memory state
```

Hash equality, stored verdict equality, or candidate self-reported provenance is
not enough.

## Required Provenance

Future executable evidence must record callable producers for:

- environment generation;
- train/heldout split generation;
- oracle policy;
- candidate behavior;
- every baseline;
- every intervention;
- leakage scan and positive controls;
- replay recomputation;
- failure taxonomy;
- final aggregation.

Every score must record input artifacts, run id, seed/context/episode ids,
aggregation rule, and code path hash.

## Acceptance For This Contract

This contract is accepted only if campaign validation confirms:

- it contains hidden latent state requirements;
- it contains train/heldout seed requirements;
- it contains heldout task-family requirements;
- it contains intervention requirements;
- it preserves the strongest baseline battery;
- it contains failure taxonomy requirements;
- it explicitly rejects task size as a substitute for learning/exploration;
- it does not authorize candidates, Phase 3, route tournament, runtime/EGO
  mainline, push, tag, commit, or remote anchor.

## Claim Ceiling

This contract is only a problem-representation redesign contract.

It does not prove:

- mechanism validity;
- learning/adaptation success;
- agency or selfhood proxy success;
- self-awareness;
- subjective experience;
- real emotion;
- autonomy;
- EGO readiness;
- companion readiness;
- runtime or mainline effect;
- route exhaustion.

## Next Minimal Closed-Loop Action

Validate this contract locally, run read-only reviewer audit, and only after
audit success open a separate Phase2C executable harness task card.
