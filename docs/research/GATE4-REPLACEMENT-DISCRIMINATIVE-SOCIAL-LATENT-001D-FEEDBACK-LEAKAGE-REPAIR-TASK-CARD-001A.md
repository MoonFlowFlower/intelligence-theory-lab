# GATE4-REPLACEMENT-DISCRIMINATIVE-SOCIAL-LATENT-001D-FEEDBACK-LEAKAGE-REPAIR-TASK-CARD-001A

Task ID: GATE4-REPLACEMENT-DISCRIMINATIVE-SOCIAL-LATENT-001D-FEEDBACK-LEAKAGE-REPAIR-TASK-CARD-001A

Mode: Draft-only targeted repair planning. This card does not authorize 001D
implementation, experiments, source edits, tests, artifact generation, Gate5,
admission, bridge, runtime, EGO-mainline, UI, LLM, AIRI, relationship, emotion,
deployment, or external services.

## Problem Definition

001C removed the 001B `baseline_hint` observation-surface leak but introduced
an equivalent split-design leak through the candidate-visible feedback channel:

```text
query_feedback = "prefers:{target}"
```

The candidate then extracts the target by parsing the feedback string. Because
the scanner and recoverability checks inspect observation-only bundles, they do
not test the actual channel used by the candidate. A future 001D repair must
test whether candidate advantage survives when feedback is not a verbatim target
label and when baselines receive equivalent query budget where relevant.

Wrong objective:

```text
Patch 001C until it passes again.
```

Correct objective:

```text
Create a bounded future repair task that can fail if candidate success is
explained by direct stated-preference copying, feedback-as-answer shortcuts, or
missing query-capable baselines.
```

## Current Stage

Draft-only repair card. No 001D implementation is authorized by this document.

## Source Negative Evidence Constraint

001D must preserve and cite:

- `docs/research/CLAUDE-INDEPENDENT-EVIDENCE-AUDIT-GATE4-REPLACEMENT-DISCRIMINATIVE-SOCIAL-LATENT-001C.md`
- `artifacts/gate4_replacement_discriminative_social_latent_001c_negative_audit_preservation_001a/result.json`
- `artifacts/gate4_replacement_discriminative_social_latent_001c_negative_audit_preservation_001a/blocked_routing_record.json`
- 001B blocked-routing negative evidence at parent boundary `e4b2f180a8a9643fc6fb45383855051ec8d4c310`
- 001C blocked candidate commit `fec4b7f8847c26116918ee9871851543515fdd6a`

001B and 001C may not be used as positive replacement-Gate4 evidence.

## Hypothesis

A future 001D harness may become more discriminative only if candidate-visible
feedback is partial, noisy, ambiguous, non-label-bearing, and insufficient for
single-token target recovery, while the candidate still beats query-capable
baselines through multi-step state integration.

This is a bounded mechanism-proxy hypothesis only. It is not evidence of
agency, selfhood, consciousness, emotion, autonomy, relationship learning, user
benefit, Gate5 readiness, admission readiness, bridge readiness, runtime
readiness, or EGO-mainline readiness.

## Required Repair Scope

1. Include `feedback_history` in the scanned evidence bundle and target
   recoverability surface.
2. Make the leakage scanner scan actual candidate-visible feedback, not only
   observations.
3. Add positive-control contamination that targets the real feedback path used
   by the candidate.
4. Add a query-and-follow-feedback baseline that receives the same query budget
   and candidate-visible feedback interface.
5. Block any candidate path that receives a verbatim target, target alias, class
   name, cyclic label, deterministic reversible label, or single-token answer
   through feedback.
6. If feedback is allowed, make it partial, noisy, ambiguous, non-label-bearing,
   and insufficient for direct action classification.
7. Give relevant baselines equivalent query budget and feedback access.
8. Keep oracle/leak positive controls clearly separated from ordinary baselines
   and from the candidate.

## Baseline Requirement

001D must include and invoke at least:

- observation-only decoder challenger;
- query-and-follow-feedback baseline;
- direct stated-preference copier;
- feedback-token lookup baseline;
- history/order/cache baselines;
- stream-keyed count table;
- graph lookup;
- transition table;
- successor map;
- count table;
- FSM planner;
- episodic traversal;
- partner/profile lookup baseline if any partner/profile signal exists;
- oracle label positive control;
- leakage positive control.

Candidate must beat the strongest ordinary baseline and the strongest
query-capable baseline by predeclared margins. If query-and-follow-feedback
ties candidate, 001D must block as baseline-equivalent.

## Ablation Requirement

001D ablations must distinguish:

- real multi-step integration;
- direct stated-preference copying;
- feedback-as-answer shortcut;
- no query;
- no feedback;
- shuffled feedback;
- counterfactual feedback;
- noisy feedback;
- partial feedback;
- feedback-token deletion;
- serialized-state replay mismatch.

A pass must be blocked if candidate reaches `1.0` by reading any single
feedback token or deterministic transform of a feedback token.

## Trace / Replay Requirement

Replay must recompute candidate query, feedback processing, state update, and
final action from serialized state, observation, feedback history, and legal
history. Corruption controls must mutate candidate-visible feedback and
serialized state, then recompute rather than returning a static failure.

## Leakage Requirement

The scanner must run on the unsanitized candidate-visible bundle containing:

- observation;
- legal history;
- feedback history;
- query action;
- serialized state before and after update;
- final action.

The scanner must detect forbidden field names, target values, target aliases,
class names, cyclic labels, reversible transforms, and direct action-token
feedback. Positive controls must contaminate the same feedback field that the
candidate consumes.

## Computed Provenance Requirement

Every score-bearing result must bind to callable producers, input artifacts,
run ID, seed/context/episode IDs, aggregation rule, computed scores, code path
hashes, and artifact pointers. Static pass flags, handwritten score reports,
and field-presence-only provenance must block.

## Acceptance Gate

001D may pass only if:

1. feedback-history leakage scanning is active on the real candidate-visible
   feedback path;
2. feedback recoverability remains below a predeclared ceiling;
3. observation-only and feedback-aware decoders cannot recover target above the
   allowed ceiling;
4. query-and-follow-feedback baseline does not tie or beat candidate;
5. candidate beats history/order/cache and partner/profile baselines where
   applicable;
6. ablations distinguish multi-step integration from copying;
7. candidate does not reach `1.0` by reading a single feedback token;
8. oracle and leak positive controls still score high and remain separated from
   ordinary evidence;
9. replay recomputes under corrupted state and feedback controls;
10. old 001B and 001C artifacts are not modified;
11. no downstream authorization flag is true.

## Stop Condition

Stop and preserve negative evidence if:

- feedback carries a verbatim target, alias, class name, cyclic label, or
  deterministic reversible answer;
- scanner excludes candidate-visible feedback;
- positive controls do not contaminate the real feedback path;
- query-and-follow-feedback ties candidate;
- candidate reaches `1.0` through a single feedback token;
- implementation requires modifying old 001B artifacts, 001C source/tests, or
  001C artifacts;
- any Gate5, admission, bridge, runtime, or EGO-mainline authorization appears.

## Rollback Plan

If a future 001D implementation modifies out-of-scope files, revert only those
changes and preserve the negative evidence. If feedback leakage cannot be
repaired without collapsing candidate performance, report the failure as
informative negative evidence rather than tuning thresholds.

## Claim Ceiling

Draft-only targeted 001D repair planning. No 001D implementation evidence,
replacement Gate4 validity, Gate5 readiness, admission readiness, bridge
readiness, runtime readiness, EGO-mainline readiness, agency, selfhood,
consciousness, emotion, autonomy, relationship learning, or user benefit is
authorized.

## What This Cannot Prove

This repair card does not prove 001D will pass, that 001C is positive evidence,
that replacement Gate4 is valid, or that any social-latent mechanism works
outside a future bounded toy harness.
