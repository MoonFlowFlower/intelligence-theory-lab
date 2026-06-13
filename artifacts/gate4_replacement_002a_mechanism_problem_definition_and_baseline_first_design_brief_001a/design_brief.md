# GATE4-REPLACEMENT-002A Mechanism Problem Definition And Baseline-First Design Brief

Task ID: GATE4-REPLACEMENT-002A-MECHANISM-PROBLEM-DEFINITION-AND-BASELINE-FIRST-DESIGN-BRIEF-001A

Mode: Governance/design brief only.

Layer: mechanism-hypothesis design plus engineering governance. This is not an executable Gate4 experiment.

## Conclusion

The next Gate4 replacement should not be another static social puzzle, bundle repair, field-hiding repair, or candidate-specific decoder-avoidance task. The strongest current explanation for the 001D route is not a working social-latent mechanism; it is target recoverability from faithful non-mechanism surfaces. 001E showed the candidate tied faithful baselines at 1.0, and 001F closed 001D-derived repair routes.

The recommended future route is a dynamic partner-belief POMDP route: a bounded environment where partner dynamics shift after interaction history, the candidate must update a self/other latent state from behavior rather than identity labels, and the decisive tests are heldout partner dynamics, counterfactual partner responses, interventions on the latent update path, and fair baseline non-equivalence.

This task only defines the problem and evidence contract for a future task card. It does not implement a harness, produce social-latent evidence, or authorize Gate5, admission, bridge, runtime, EGO-mainline, UI, companion, autonomy, selfhood, emotion, or consciousness claims.

## Closure Inheritance From 001E And 001F

001E is inherited as negative evidence:

- candidate score: 1.0
- pair_count_table score: 1.0
- full-bundle decoder score: 1.0
- serialized-state decoder score: 1.0
- strongest faithful baseline: pair_count_table
- stop condition: pair_count_table_tied_candidate

001F closed 001D-derived repair attempts because the 001D target was recoverable through faithful task encodings and candidate-visible surfaces. The closed route family includes continuing to patch 001D, bundle/feedback repairs that preserve target-bearing encodings, candidate-specific puzzle construction, and denying baselines candidate-equivalent access.

The inherited conclusion is narrow: the 001D route failed structurally. It does not prove that no social-latent mechanism is possible. It does prove that a future Gate4 design must be baseline-first and must define the non-mechanism baselines before candidate success criteria.

## Error In The Prior Problem Definition

Wrong problem:

```text
Can a candidate solve a compact social puzzle better than weak baselines?
```

Why this is wrong: a compact target can be encoded in observations, feedback, serialized state, bundle fields, partner IDs, pair counts, trace surfaces, or fixture structure. If a faithful decoder recovers the target, the task is testing encoding recovery rather than social-latent mechanism.

Better problem:

```text
Under partial observability and partner changes, can the agent maintain and update separate self/other latent state from behavior, use that state to predict and act under changed conditions, and degrade under real interventions on the social-latent update path in ways fair non-mechanism baselines cannot match?
```

## Anti-Sycophancy Audit

Strongest baseline explanation: a pair-count table, trace lookup, partner-ID lookup, full-bundle decoder, serialized-state decoder, finite-state policy, preference table, query-capable imitation baseline, belief table, or non-social world model may reproduce apparent social behavior without a social-latent mechanism.

Strongest reason this task may be invalid: even a dynamic toy environment can collapse if partner changes are enumerable, target labels leak through context IDs or observations, the candidate receives information denied to baselines, or the evaluation rewards action matching rather than intervention-sensitive state updates.

What would falsify this framing: if the proposed dynamic partner-belief route cannot be specified without compact partner identifiers, explicit preference labels, answer-bearing observations, or candidate-specific puzzle structure, then the route should be rejected and Gate4 should be deferred.

Evidence that would still be insufficient: a high aggregate candidate score, a readable latent-state trace, post-hoc explanations, static heldout label accuracy, or replay hashes alone would not be sufficient. The future task would need fair baseline non-equivalence, real ablation degradation, counterfactual sensitivity, leakage positive controls, and replay recomputation from serialized state plus observation.

Mechanism or behavioral resemblance: this design targets future mechanism-proxy evidence. The present task produces only a design contract. It does not test a mechanism.

## New Gate4 Mechanism Target

The candidate target for a future executable task should require all of the following:

- maintain separate self-state and other-state representations;
- update other-state from observed behavior, not partner ID, labels, filenames, fixture names, or explicit preference tokens;
- predict partner behavior under changed conditions;
- adapt after partner policy shift or preference shift;
- choose actions based on inferred partner latent state;
- expose traceable latent updates or state snapshot hashes;
- replay from serialized state plus observation;
- fail or degrade under real ablation of the social-latent update path.

The target is dynamic adaptation and counterfactual response, not static puzzle solving.

## Explicit Non-Targets

The future design must not target:

- pair-count table recoverability;
- full-bundle decoding;
- serialized-state decoding;
- partner-ID lookup;
- trace-only lookup;
- menu preference table memorization;
- finite-state script keyed by visible tokens;
- candidate-specific puzzle solving;
- hidden target recovery;
- answer-label recovery;
- evaluator-only obfuscation;
- encryption, field renaming, or language/runtime switching;
- withholding target-bearing fields from baselines while the candidate keeps equivalent information.

## Baseline-First Adversarial Design

Baselines must be specified before candidate success criteria. Each baseline must be an independent callable implementation with fair access rights.

Minimum required future baselines:

- random/control baseline;
- pair-count baseline;
- n-gram/trace lookup baseline;
- partner-ID baseline;
- preference-table baseline;
- full-bundle decoder;
- serialized-state decoder;
- finite-state policy baseline;
- query-capable imitation baseline;
- belief-table baseline;
- oracle-access upper bound;
- ablated-candidate baseline with social-latent update disabled;
- non-social world-model baseline, where the environment includes non-social transition structure.

Additional collapse-family controls should be considered where representational or environment claims are made: graph_lookup, transition_table, successor_map, count_table, fsm_planner, episodic_traversal, nearest-neighbor, RAG/summary memory, and shuffled-history controls.

The future candidate success metric is not valid unless the strongest faithful baseline is identified and the candidate advantage survives under heldout partner dynamics and counterfactual intervention tests.

## Candidate Mechanism Contract

A future candidate may use explicit, learned, or high-dimensional latent representations only if the experiment remains auditable. Complete human semantic labeling of every latent component is not required, but the future task must record the update history, observation stream, state snapshots or hashes, action distributions or decisions before/after updates, and replay inputs.

The candidate contract must include:

- self_state and other_state separation;
- update rule invoked after partner behavior observations;
- no direct use of partner ID as the latent state key;
- prediction before observing partner response;
- action selection conditioned on inferred other_state;
- intervention hooks for freezing, shuffling, deleting, replacing, or corrupting the social-latent update path;
- deterministic seed or predeclared statistical equivalence rules;
- serialized state sufficient for replay recomputation.

## Heldout And Counterfactual Structure

The future task must include:

- heldout partner dynamics, not only heldout labels;
- partner policy shifts after interaction history;
- counterfactual partner response tests;
- intervention on candidate social-latent state;
- intervention on partner-observation stream;
- train, heldout, and counterfactual context IDs;
- at least one positive-control leakage case;
- at least one negative-control no-signal case.

The key split should not be "same puzzle, hidden answer." It should be a dynamic split: the partner's latent rule changes or transfers across contexts in ways a static count table or partner-ID lookup should not generalize to unless it is effectively modeling the same update structure.

## Replay And Provenance Contract

Future executable evidence must be computed through callable paths, not literals or static pass reports. Every reported result, baseline, ablation, contrast, leakage, and replay metric must record:

- producer_function;
- input artifacts;
- run_id;
- seed, context, and episode IDs;
- aggregation rule;
- code path hash;
- candidate-visible access manifest;
- baseline access manifest;
- replay state source and hash;
- intervention manifest.

Replay must recompute candidate behavior from serialized_state plus observation. Hash-only trace replay is insufficient. Ablations must rerun episodes under real interventions.

## Failure Routing Policy

Route as failure or block if any of the following occur:

- a pair-count, full-bundle, serialized-state, trace lookup, partner-ID, or preference-table baseline ties the candidate under fair access;
- success depends on encryption, obfuscation, field renaming, runtime switching, or evaluator-only concealment;
- the target is encoded in observations, action names, context IDs, fixture paths, serialized state, bundle fields, trace records, or answer labels;
- candidate and baselines do not receive fair information access;
- replay cannot recompute from serialized state plus observation;
- social-latent ablation does not degrade the claimed behavior;
- positive-control leakage does not fail when leakage is injected;
- no reasonable route can avoid decoder-collapse risk at bounded complexity.

If no route avoids decoder-collapse risk at reasonable complexity, defer Gate4 and return to cross-gate theory coverage.

## Decision Matrix Summary

| Route | Recommendation | Main reason |
| --- | --- | --- |
| Dynamic partner-belief POMDP | Recommended | Best bounded path for self/other state updates, partner shifts, counterfactuals, replay, and ablation clarity. |
| Active-inference / self-other belief | Not next | Mechanism-relevant, but easier to over-abstract before a concrete baseline-resistant environment exists. |
| Predictive world-model / social transition | Not next | Useful fallback, but risks becoming a non-social transition model unless partner-latent tests are primary. |
| Causal-intervention social latent | Not next | Strong intervention discipline, but too narrow as a full problem definition without dynamic partner-belief scaffolding. |
| Defer Gate4 and return to cross-gate theory coverage | Fallback only | Correct if all Gate4 routes remain decoder-collapsible, but premature before one bounded dynamic route is specified. |

At least one route is rejected for puzzle/decoder-collapse risk: static puzzle or 001D-derived puzzle variants remain closed, and predictive world-model-only variants are rejected unless they include social-latent heldout/intervention structure.

## Recommended Next Executable Task Card

Recommend exactly one next task card:

```text
GATE4-REPLACEMENT-002B-DYNAMIC-PARTNER-BELIEF-POMDP-EXECUTABLE-TASK-CARD-001A
```

This future card should specify an isolated dynamic partner-belief POMDP harness, but 002A does not create or execute that harness. The 002B card must freeze environment generation, baselines, ablations, leakage scans, replay, provenance, claim ceiling, and stop/rollback policy before any source code is edited.

## Claim Ceiling

Allowed claims:

- bounded Gate4 replacement problem-definition reset;
- baseline-first design constraints;
- recommendation for a future executable task card.

Forbidden claims:

- valid Gate4;
- social-latent inference evidence;
- mechanism validity;
- agency;
- selfhood;
- consciousness;
- emotion;
- autonomy;
- EGO readiness;
- stable user benefit.

## What This Does Not Prove

This does not prove that Dynamic Partner-Belief POMDP is sufficient, that any social-latent mechanism works, that future baselines will be defeated, or that any system has agency, selfhood, consciousness, emotion, autonomy, EGO readiness, or user benefit.
