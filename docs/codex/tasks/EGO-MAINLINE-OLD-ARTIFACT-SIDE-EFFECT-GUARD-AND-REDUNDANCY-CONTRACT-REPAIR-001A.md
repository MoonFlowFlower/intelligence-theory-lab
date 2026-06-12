# EGO-MAINLINE-OLD-ARTIFACT-SIDE-EFFECT-GUARD-AND-REDUNDANCY-CONTRACT-REPAIR-001A

## Layer

Evidence-governance / bounded repair only.

This task repairs evidence hygiene defects only. It does not enter Gate4,
bridge runtime, EGO runtime, mechanism implementation, product behavior, LLM
integration, relationship learning, emotion systems, or deployment.

## Problem Definition

Known-failure triage 001A sealed four full-suite failures after commit
`c9bee968069f9d218c0c45a37efba092e4535156`.

The two persistent failures are redundancy/temp-run failures where downstream
readback artifacts are being treated as duplicate contract definitions before
the callable validators execute.

The two order-dependent failures are repo-hygiene failures where old artifact
generation can write live dirty-state observations into sealed artifacts,
changing later routing and dependency-closure outcomes.

## Current Stage

Post-triage bounded repair before any Gate4 task-card drafting can be
considered.

## Hypothesis

A valid repair should:

- make temp-run and canonical runs use the same callable validator contracts;
- prevent downstream readback or trace artifacts from blocking temp validator
  execution as redundant contract definitions;
- isolate old artifact corruption and positive controls in temp outputs or
  in-memory state;
- prove old sealed artifacts are unchanged by before/after hash comparison.

## Baselines

- `naive_targeted_repair_baseline`: targeted known-node rerun only; unsafe
  because it can miss full-suite order effects.
- `naive_restore_after_mutation_baseline`: allows mutation and restores after;
  unsafe because it hides side effects.
- `strict_no_old_artifact_write_baseline`: blocks if old sealed artifact paths
  are written during repair tests.
- `claim_ceiling_baseline`: blocks Gate4, runtime, bridge, implementation,
  mechanism, theory, agency, selfhood, consciousness, emotion, relationship
  learning, and stable user benefit claims regardless of test status.

## Ablations

The repair verification must rerun under interventions that disable the write
guard, replace temp-copy output with real sealed output, use a dummy validator,
remove hash checks, remove cleanup, substitute corrupted positive controls, run
targeted tests without full-suite observation, and inject an unauthorized
readiness claim.

## Trace / Replay Requirement

`repair_state.json` must serialize observations, anchors, known failed node IDs,
before-repair reproduction, repair parameters, file-change inventory, hash
inventory, side-effect guards, targeted/full-suite observations, `run_id`, and
seed/context identifiers.

Replay must recompute the repair verdict, residual failure classification, and
route impact from serialized state plus observation. It must not only compare
stored verdict strings or hashes.

## Acceptance Gate

Pass only if the c9bee968 triage anchor and remote tag verify, the four known
failed node IDs are reproduced or explicitly marked non-reproducible with
evidence, temp-run validators execute through the same callable contracts,
old sealed artifacts are not mutated in final state, baselines and ablations are
invoked, the leakage scanner detects a positive control, replay recomputes, and
full pytest passes or residual failures are classified as blockers.

## Claim Ceiling

Bounded evidence-hygiene repair evidence at governance layer only.

## Stop Conditions

Stop if anchors cannot be verified, old sealed artifacts must be rewritten,
tests can only pass by deleting/skipping/weakening assertions, shared validator
equivalence cannot be proven, corruption tests still mutate sealed artifacts,
full pytest cannot be run without bounded observation, provenance is static,
baseline/ablation/replay/leakage gates fail, or generated artifacts authorize
any downstream route.

## Rollback Plan

Revert any source or test change that weakens assertions, restore any
test-created old artifact mutation, preserve generated failure artifacts under
the 001A artifact directory, report exact residual failures, and do not convert
blocked routes into a pass.

## What This Does Not Prove

This does not prove EGO readiness, bridge readiness, runtime readiness, Gate4
readiness, mechanism validity, theory validity, architecture correctness,
agency, selfhood, consciousness, emotion, relationship learning, stable user
benefit, future runtime correctness, or downstream authorization.
