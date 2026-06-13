# GATE4-REPLACEMENT-002C Dynamic Partner-Belief POMDP Execution

Task ID: GATE4-REPLACEMENT-002C-DYNAMIC-PARTNER-BELIEF-POMDP-EXECUTION-001A

Parent drafting task: GATE4-REPLACEMENT-002B-DYNAMIC-PARTNER-BELIEF-POMDP-EXECUTABLE-TASK-CARD-001A

Allowed layer: engineering implementation plus mechanism-hypothesis testing.

Forbidden upgrade: no Gate5, admission, bridge, runtime, EGO-mainline, companion/product UX, agency, selfhood, consciousness, real emotion, autonomy, or stable user benefit claim.

## Problem Definition

Implement and execute an isolated dynamic partner-belief POMDP-style Gate4 replacement experiment. The experiment must test whether a candidate can maintain and update bounded self/other latent state from observed partner behavior under partial observability, partner policy shifts, heldout partner dynamics, and counterfactual probes.

The task is not to make behavior look social. It is to determine whether candidate behavior remains non-equivalent to faithful non-mechanism baselines when every score, baseline, ablation, leakage scan, and replay metric is computed by callable paths.

## Current Stage

002C starts after 002B task-card drafting and must inherit:

- 001D-derived repair route remains closed.
- 001E is preserved as baseline-equivalence negative evidence.
- 001F closed 001D-derived patching and reset the problem definition.
- 002A selected dynamic partner-belief POMDP as the next bounded route only after baseline-first constraints.
- 002B froze this executable card and supporting governance contracts before code edits.

## Mechanism Hypothesis

A bounded social-latent mechanism should update an internal other-state from observed partner behavior, distinguish self-state from other-state, adapt when partner policy shifts after interaction history, predict partner behavior under changed conditions, and choose actions conditioned on inferred partner state.

The candidate is meaningful only if success cannot be recovered from partner ID, visible labels, pair counts, bundle fields, serialized state, trace ordering, menu preference tables, fixed finite-state scripts, or answer labels.

## Strongest Baseline Explanation

The strongest baseline explanation is that apparent social adaptation is produced by lookup or decoding: pair counts, n-gram trace lookup, partner-ID lookup, preference tables, full-bundle decoding, serialized-state decoding, finite-state policy, query-capable imitation, belief tables, or a non-social world model.

002C must implement these baselines before accepting candidate metrics.

## Strongest Reason This Task May Be Invalid

The POMDP can still collapse if partner latent type, policy shift, target label, reward signal, or hidden state is encoded in visible observations, filenames, context IDs, partner IDs, action names, serialized state, trace order, bundle fields, or fixture structure.

If that happens, 002C must report baseline-equivalence or leakage failure instead of patching thresholds.

## What Would Falsify The Current Framing

The framing fails if:

- a faithful callable non-mechanism baseline ties or exceeds the candidate on heldout or counterfactual partner dynamics;
- positive-control leakage is not detected;
- no-signal negative control allows false success;
- social-latent ablation does not degrade candidate behavior;
- replay cannot recompute behavior from serialized state plus observation;
- fair faithful baselines cannot be defined without denying them candidate-equivalent access.

## Evidence That Would Still Be Insufficient

The following are insufficient: high aggregate score, a plausible latent trace, post-hoc interpretation, stored action replay, stored metric replay, replay hashes, schema validation, or tests that assert pass. 002C requires callable computation, fair baselines, real rerun ablations, leakage positive controls, no-signal negative controls, and replay recomputation.

## Environment Contract

The environment must include:

- partial observability;
- at least two partner latent types;
- at least one partner policy shift after interaction history;
- heldout partner dynamics;
- counterfactual partner response probes;
- intervention on candidate social-latent state;
- intervention on partner-observation stream;
- negative-control no-signal condition;
- positive-control leakage condition;
- explicit train, heldout, counterfactual, and ablation context IDs.

The target must not be directly recoverable from partner ID, visible labels, pair counts, bundle fields, serialized state, trace ordering alone, menu preference tables, fixed finite-state scripts, or answer labels.

## Candidate Mechanism Contract

The candidate must:

- maintain separate self-state and other-state representations;
- update other-state from observed behavior rather than partner ID;
- expose traceable latent updates or auditable state snapshots;
- predict partner behavior under changed conditions before observing the response;
- adapt after partner policy or preference shift;
- choose actions based on inferred partner latent state;
- replay behavior from serialized state plus observation;
- degrade under ablation of the social-latent update path.

The candidate must not receive privileged target labels, evaluator-only fields, or access surfaces unavailable to fair baselines.

## Baseline Contract

002C must implement independent callable baselines before candidate scoring:

- random/control baseline;
- pair-count baseline;
- n-gram / trace lookup baseline;
- partner-ID baseline;
- preference-table baseline;
- full-bundle decoder;
- serialized-state decoder;
- finite-state policy baseline;
- query-capable imitation baseline;
- belief-table baseline;
- oracle-access upper bound;
- ablated-candidate baseline with social-latent update disabled;
- non-social world-model baseline.

Each baseline report must record producer function, input artifacts, run ID, seed, train context IDs, heldout context IDs, counterfactual context IDs, episode IDs, aggregation rule, code path hash, access-rights declaration, and failure mode ruled out.

If any faithful non-oracle baseline ties or exceeds the candidate under fair access on accepted metrics, classify the result as baseline-equivalence negative evidence.

## Ablation Contract

002C ablations must be real reruns under interventions, not report-only edits.

Required ablations:

- disable social-latent update path;
- freeze other-state after initial observation;
- shuffle partner-observation history;
- remove partner policy shift;
- swap partner latent dynamics;
- mask partner ID and explicit labels;
- inject target leakage as positive control;
- remove social signal as negative control.

Each ablation must rerun the candidate and relevant baselines.

## Heldout And Counterfactual Contract

002C must define explicit train, heldout, counterfactual, and ablation context IDs. Context IDs are required for traceability, but must be audited so they cannot encode target labels, partner type, or policy shift.

Heldout must be heldout partner dynamics, not only heldout labels. Counterfactual probes must alter partner response structure while controlling non-causal surfaces where possible.

## Replay Contract

Replay must recompute candidate and baseline behavior from serialized state plus observation. Replay is invalid if it only compares stored hashes, stored actions, stored predictions, or stored metrics.

Each replay row must record:

- serialized state path;
- observation path;
- recomputation function;
- replay run ID;
- expected action or prediction;
- actual recomputed action or prediction;
- comparison rule;
- replay failure-path test.

## Computed-Evidence Provenance Gate

002C must block any result where scores, baselines, ablations, leakage scans, or replay metrics come from literals, static dictionaries, unconditional clean reports, unused seeds, unused train contexts, unused heldout contexts, unused counterfactual contexts, declared but uninvoked baselines, declared but unrerun ablations, leakage scanners without positive-control cases, or replay that does not recompute behavior.

Every score must record:

- producer function;
- input artifacts;
- run ID;
- seed;
- context IDs;
- episode IDs;
- aggregation rule;
- code path hash.

## Leakage-Positive-Control Gate

002C must include at least one positive-control leakage condition where target or partner-latent information is deliberately injected into candidate-visible surfaces. The scanner must detect it. If the scanner misses the injected leakage, the 002C result is blocked.

002C must also include at least one negative-control no-signal condition. If candidate or non-oracle baselines exceed allowed chance or declared prior performance in the no-signal condition, the result is blocked.

## Failure-Path Tests Required For 002C

002C must include tests that fail on:

- missing baseline invocation;
- missing ablation rerun;
- static score dictionary injection;
- unused seed;
- unused train, heldout, counterfactual, or ablation context;
- leakage-positive-control miss;
- no-signal false success;
- replay that compares hashes only;
- replay that reuses stored actions or stored metrics;
- candidate-only privileged access;
- fair baseline tying or beating candidate.

## Acceptance Gate

PASS only if:

- candidate beats strongest faithful non-mechanism baseline on heldout and counterfactual partner dynamics;
- full-bundle decoder and serialized-state decoder fail below candidate under fair access;
- pair-count, partner-ID, trace-lookup, finite-state, and belief-table baselines fail below candidate;
- ablated candidate degrades meaningfully;
- positive-control leakage is detected;
- negative-control no-signal condition blocks false success;
- replay recomputes behavior from serialized state plus observation;
- all baselines and ablations are callable and invoked;
- provenance is complete;
- failure-path tests are present;
- no Gate5/admission/bridge/runtime/EGO-mainline files are changed.

## Claim Ceiling

Allowed claim if all gates pass: bounded offline mechanism-proxy evidence for the named dynamic partner-belief POMDP experiment, with baseline non-equivalence, ablation sensitivity, leakage resistance, and replay recomputation under the declared split.

Forbidden claims: valid Gate4 in general, social-latent inference proof, mechanism validity in general, agency, selfhood, consciousness, emotion, autonomy, EGO readiness, companion readiness, stable user benefit, Gate5 readiness, admission readiness, bridge readiness, runtime readiness, or proof that Bio-CMBC, CVPSM, VCCO, CMBC, or R/G is correct.

## Stop Condition

Stop and preserve a blocked report if:

- the design depends on encryption, obfuscation, field hiding, partner-ID lookup, answer-label recovery, trace-only lookup, or candidate-specific puzzle construction;
- the future 002C implementation changes Gate5, admission, bridge, runtime, EGO-mainline, UI, companion behavior, relationship learning, emotion systems, proactive behavior, LLM integration, AIRI integration, deployment, API keys, or external services;
- fair faithful baselines cannot be defined;
- source modules or tests are created outside the isolated 002C paths allowed by the eventual 002C card;
- prior 001D/001E/001F/002A/002B artifacts are mutated.

## Rollback Plan

If 002C creates out-of-scope files, reverts must remove those files and preserve a blocked report. If prior artifacts are mutated, revert the mutations and preserve a blocked report. If baseline equivalence, leakage, no-signal false success, replay failure, or ablation non-degradation occurs, do not patch thresholds; report the failed condition as evidence.

## Non-Claims

002C cannot prove subjectivity, real agency, consciousness, real emotion, autonomy, companion readiness, EGO readiness, or stable user benefit. Even a pass remains bounded offline mechanism-proxy evidence for one declared test.
