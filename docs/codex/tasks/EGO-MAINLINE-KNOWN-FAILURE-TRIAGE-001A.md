# EGO-MAINLINE-KNOWN-FAILURE-TRIAGE-001A

## Mode

Known failure triage / reproducibility classification / blocker severity audit
only.

## Layer

Evidence-governance / known-failure triage only.

This task does not repair tests, patch old artifacts, rewrite historical
verdicts, enter Gate4, enter bridge runtime, enter EGO runtime implementation,
or create product, companion, LLM/RAG, user-model, memory, relationship,
emotion, or runtime work.

## Problem Definition

Given that `EGO-MAINLINE-EVIDENCE-DEPENDENCY-CLOSURE-001A` classified known
failures as the next blocker, identify the exact failing tests, reproduce or
refute each failure, classify failure cause and blocker severity, explain the
difference between prior full-suite failure counts and the known-failure probe,
and recommend the next bounded task without repairing anything.

## Current Stage

Post-dependency-closure known-failure triage.

## Hypothesis

The current failures are governance/redundancy/temp-run/sealed-artifact
consistency blockers and side-effect-sensitive clean-state failures, not direct
failures of the new post-admission routing or dependency-closure artifacts.
This must be computed from current test evidence rather than assumed.

## Strongest Baseline Explanation

The strongest unsafe baseline is targeted green advancement: targeted routing
and dependency-closure tests can pass while full-suite failures remain.

## Strongest Reason This Task May Be Invalid

This task can only classify failures. It cannot make old tests pass, prove
mechanism validity, validate theory, authorize Gate4, or authorize runtime
implementation.

## Falsification Condition

The framing is falsified if required anchors do not verify, full pytest cannot
be observed or captured as a blocker, failed node IDs cannot be identified,
isolated reruns are missing without explanation, the full-suite/probe
discrepancy remains unexplained, a failure is caused by new 001A work, old
artifacts are mutated and not restored, baselines or ablations are skipped,
leakage positive control is missed, replay does not recompute, or any output
authorizes downstream runtime, Gate4 execution, implementation, mechanism
validity, theory validity, architecture correctness, agency, selfhood,
consciousness, emotion, relationship learning, or stable user benefit.

## Insufficient Evidence

Passing this triage remains insufficient evidence for EGO readiness, bridge
readiness, runtime readiness, Gate4 readiness, mechanism validity, theory
validity, architecture correctness, agency, selfhood, consciousness, emotion,
relationship learning, stable user benefit, future runtime correctness, or
runtime authorization.

## Mechanism Test Classification

This is not a mechanism test and does not produce behavioral resemblance. It is
a governance-layer failure triage and blocker classification only.

## Baselines

1. `naive_targeted_tests_green_baseline`
   - Uses only targeted routing/dependency-closure test results.
   - Unsafe tendency: ignores full-suite failures.

2. `naive_unrelated_old_failure_baseline`
   - Treats all pre-existing failures as unrelated.
   - Unsafe tendency: under-classifies blockers.

3. `strict_full_suite_failure_baseline`
   - Blocks downstream advancement if any full-suite failure remains.

4. `claim_ceiling_baseline`
   - Uses claim ceiling and non-proven list only.
   - Blocks runtime, bridge, Gate4 execution, implementation, and stronger
     mechanism/theory/agency claims.

## Ablations

Rerun candidate triage after removing or substituting full pytest observation,
failed node IDs, isolated reruns, traceback text, hash inventory, side-effect
report, prior dependency-closure classification, claim ceiling, route
permission matrix, clean targeted-only observations, new-001A-caused failures,
old-artifact mutation failures, and positive-control unauthorized readiness
claims.

No ablation may authorize runtime, bridge runtime, Gate4 execution, EGO
implementation, mechanism validity, theory validity, architecture correctness,
agency, selfhood, consciousness, emotion, relationship learning, or stable user
benefit.

## Trace / Replay Requirement

Create `triage_state.json` containing observations, anchor readbacks, full
pytest result, failed node IDs, isolated rerun results, traceback summaries,
hash inventory digest, side-effect report, dependency closure inputs, triage
parameters, run id, and seed/context identifiers if used.

Replay must recompute triage from serialized state plus observation and match
triage verdict, failed-node classification, blocker severity, route impact, and
reason codes. It must not compare only hashes or stored verdict strings.

## Computed-Evidence Provenance Gate

Every result, baseline result, ablation result, leakage result, replay result,
blocker score, route impact score, failure category, and verdict-like value must
come from callable computation paths. Each must record producer function, input
artifacts, run id, seed/context identifiers, aggregation rule, code path hash,
and output artifact path.

## Acceptance Gate

Pass only if required local and remote anchors verify exactly, full pytest is
observed or a failed attempt is recorded, exact failed node IDs are captured,
each failed node is rerun or marked rerun-blocked, failure discrepancy is
explained from computed evidence, no test repair is performed, old artifacts
are not patched, test side effects are recorded and restored, triage is computed
from callable code, baselines and ablations are invoked, leakage positive
control is detected, replay recomputes, no generated artifact positively
authorizes downstream work or stronger claims, and the result contains a safe
next bounded recommendation.

## Expected Verdict Forms

- `known_failure_triage_001a_pass_with_blockers_classified`
- `known_failure_triage_001a_pass_failures_nonblocking_but_recorded`
- `known_failure_triage_001a_blocked_unexplained_failure_discrepancy`
- `known_failure_triage_001a_blocked_unclassified_failure`
- `known_failure_triage_001a_blocked_old_artifact_side_effect`
- `known_failure_triage_001a_failed_provenance_gate`
- `known_failure_triage_001a_failed_leakage_gate`
- `known_failure_triage_001a_failed_replay_gate`

## Stop Conditions

Stop and report blocked if required anchors cannot be verified, full pytest
cannot be observed and no bounded failure observation exists, exact failed node
IDs cannot be identified, isolated rerun results are missing without
explanation, the failure-count discrepancy cannot be explained, any failure is
caused by new 001A work, old artifacts are mutated and not restored, triage
authorizes forbidden downstream work, provenance is static/uncomputed,
baselines or ablations are skipped, leakage positive control is not detected,
replay only compares hashes or stored verdict strings, or repo state is dirty
for unrelated reasons.

## Rollback Plan

If blocked or failed, do not repair tests, do not patch old artifacts, do not
weaken claim ceiling, do not convert blocked routes into passes, preserve
generated failure artifacts under the 001A artifact directory, and report the
exact missing evidence, failed gate, and safe next bounded triage continuation
or repair task.

## Claim Ceiling

Bounded known-failure triage evidence at governance layer only.

## What This Does Not Prove

- EGO readiness.
- Bridge readiness.
- Runtime readiness.
- Gate4 readiness.
- Mechanism validity.
- Theory validity.
- Architecture correctness.
- Agency.
- Selfhood.
- Consciousness.
- Emotion.
- Relationship learning.
- Stable user benefit.
- Future runtime correctness.
- Runtime authorization.
