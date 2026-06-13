# FUTURE-GATE4-CROSS-FAMILY-SOCIAL-CAUSAL-TRANSFER-EXECUTION-CARD-001B

`DRAFT ONLY — NOT AUTHORIZED FOR IMPLEMENTATION`

This is an append-only revision from `CLAUDE-INDEPENDENT-AUDIT-DRAFT-FUTURE-EXECUTABLE-GATE4-DESIGN-CARD-001A`. It preserves the audit as blocking negative design evidence against 001A and revises the future Gate4 design card so the blocking baseline-collapse issues are bound in machine-readable contracts.

This card is not an implementation task, not an experiment task, not a Gate4 execution task, not 002E, and not authorization to enter Gate5/admission/bridge/runtime/EGO-mainline.

## Problem Definition

001A correctly moved the future Gate4 target away from same-family toy hardening and toward `cross_family_social_causal_transfer`. The blocking audit found that 001A still left the decisive judgment axis under-bound: it omitted the full `graph_cache_family`, omitted `query_capable_imitation_baseline`, and did not freeze candidate-vs-baseline equivalence rules.

001B fixes those blockers in binding JSON rather than prose only.

## Current Stage

Current stage: future executable design-card revision only.

Allowed current output: audit preservation, revised draft card, and machine-readable future contracts.

Forbidden current output: source code, tests, environments, candidate agents, baselines, graph-cache implementations, imitation baselines, leakage scanners, replay code, datasets, experiments, 002C reruns, 002D reruns, 002E, Gate5/admission/bridge/runtime/EGO-mainline artifacts, or mechanism success claims.

## Mechanism Hypothesis

Future execution may test only this bounded mechanism-proxy hypothesis:

```text
A future candidate performs cross-family social causal transfer only if it uses replayable hidden partner-relevant state updates to support counterfactual prediction or action under unseen partner causal families and unseen task schemas, while all faithful non-oracle baselines remain below candidate under fair callable access and a frozen equivalence rule.
```

This is an engineering hypothesis for a future executable gate, not a claim that the mechanism is valid.

## Required Revisions From Claude Audit

### F1: Restore `graph_cache_family`

Future execution must implement and invoke the full `graph_cache_family`:

- `graph_lookup`
- `transition_table`
- `successor_map`
- `count_table`
- `fsm_planner`
- `episodic_traversal`

Each member must declare access rights, producer function, input artifacts, expected shortcut, why it challenges cross-family social causal transfer, positive control or sanity check, function class, fitting budget, data access boundary, required failure or tie condition, and hard stop if it ties, beats, or is candidate-equivalent to candidate.

Any future implementation that omits one member must block.

### F2: Restore `query_capable_imitation_baseline`

Future execution must implement and invoke `query_capable_imitation_baseline`.

It must have the same query budget and same observation access as the candidate. It must not claim a belief-update mechanism. Its purpose is to detect scripted active querying, prompt-level social behavior, and imitation-based probing.

If it ties, beats, or is candidate-equivalent to candidate on primary heldout or counterfactual metrics, future execution must report negative evidence.

### F3: Freeze Candidate-Vs-Baseline Equivalence

Future execution must freeze a candidate-vs-baseline equivalence rule before any run.

Minimum rule:

- Candidate clears a faithful baseline only if candidate exceeds that baseline on the primary heldout metric under the frozen equivalence rule.
- Any faithful non-oracle baseline tie, beat, or candidate-equivalent result is negative evidence.
- Ablation drop does not rescue the claim if any faithful baseline still solves the task.
- The equivalence rule must be hashed or otherwise recorded in provenance before any future run.

Because the future metric is not implemented by this task, implementation remains blocked until a separate executable implementation card freezes a metric-specific margin or statistical rule before any run.

## Baseline Requirements

Future execution must implement and invoke independent callable baselines before candidate claims are allowed:

- `serialized_state_decoder`
- `full_bundle_decoder`
- `static_belief_table`
- `pair_count_frequency_baseline`
- `ngram_trace_lookup`
- `nearest_neighbor_trace_retrieval`
- `graph_cache_family`
- `graph_lookup`
- `transition_table`
- `successor_map`
- `count_table`
- `fsm_planner`
- `episodic_traversal`
- `query_capable_imitation_baseline`
- `label_config_leakage_scanner`
- `trace_id_episode_order_leakage_scanner`
- `schema_split_leakage_scanner`
- `majority_baseline`
- `random_baseline`
- optional `oracle_upper_bound`

Every faithful non-oracle baseline must declare function class, fitting budget, access rights, train/heldout boundary, oracle status, producer function, input artifacts, expected shortcut, and stop condition.

## Candidate-Agnostic Metric Rule

Primary metrics must not be defined in terms of candidate output schema, candidate internals, renderer-visible behavior, or post-hoc candidate explanations.

Metric producer functions, aggregation rules, thresholds, equivalence margins, and statistical rules must be frozen before any future run and recorded in provenance.

## Acceptance Gate For Future Implementation

Future implementation can pass only if:

- all frozen seeds, contexts, episodes, heldout partner families, heldout task schemas, and counterfactual pairs are consumed;
- candidate primary metric is produced by callable code;
- the metric is candidate-agnostic;
- equivalence rule is frozen and recorded in provenance;
- every faithful non-oracle baseline is invoked;
- all `graph_cache_family` members are invoked;
- `query_capable_imitation_baseline` is invoked with same query budget and observation access as candidate;
- no faithful non-oracle baseline ties, beats, or is candidate-equivalent to candidate;
- ablation drops do not mask baseline equivalence;
- replay recomputes candidate and baseline behavior;
- leakage scanners detect positive controls and report clean-artifact findings;
- provenance records producer function, input artifacts, run id, seed, context IDs, episode IDs, aggregation rule, code path hash, equivalence rule hash, and baseline access-rights declaration.

## Negative-Evidence Stop Conditions

Stop and report negative evidence or blocked status if:

- any faithful non-oracle baseline ties or beats candidate on the primary heldout metric;
- any faithful non-oracle baseline is candidate-equivalent under the frozen equivalence rule;
- any `graph_cache_family` member ties, beats, or is candidate-equivalent to candidate;
- any `graph_cache_family` member is omitted or not invoked;
- `query_capable_imitation_baseline` ties, beats, or is candidate-equivalent to candidate;
- `query_capable_imitation_baseline` is omitted, not callable, or not invoked;
- equivalence rule is missing, changed after run, selectively applied, or absent from provenance;
- ablation drop exists but a faithful baseline still solves the task;
- metric is candidate-specific or post-hoc;
- leakage positive control fails;
- replay can pass from stored outputs, stored actions, trace-only comparison, or hashes;
- task requires hiding fair candidate-visible information from baselines;
- implementation starts before this card is remote-anchored and separately authorized.

## Claim Ceiling

001B can claim only:

- preservation of Claude independent audit as blocking design evidence;
- 001B draft revision from Claude audit blockers;
- revised baseline-collapse guardrail specification;
- revised equivalence and provenance requirement specification.

It cannot claim valid Gate4, mechanism validity, social-latent inference, agency, selfhood, consciousness, emotion, autonomy, EGO readiness, runtime readiness, companion readiness, or user benefit.

## Strict Non-Actions

Do not implement Gate4, environments, candidate agents, baselines, graph-cache baselines, imitation baselines, leakage scanners, replay code, 002E, Gate5, admission, bridge, runtime, or EGO-mainline from this card.
