# M1-004 Reimplementation Readiness

Assessment: ready for an independent reimplementation contract, but not for a general LCC agent or theory-support claim.

## Why It Is Ready

- Cycle 000-010 define a clear public evidence pattern: behavior invariant under label permutation, sensitive under effect perturbation, intervention-grounded, replayable from behavior-only traces, and robust to blind holdout after candidate freeze.
- Cycle 009 reduced the risk of per-cycle specialist dispatch.
- Cycle 010 added freeze integrity, independent scoring, replication, ablation, negative controls, and generic baseline comparison.
- The minimal principle can be stated without implementation-specific runner details.

## What Must Be Independent

- Testbed implementation.
- Candidate implementation.
- Trace schema adapter or scorer.
- Holdout generation.
- Baseline implementations.
- Negative controls.
- Static leak scan.

## What May Be Reused

- Public theory card.
- Public contract requirements.
- Forbidden-input list.
- Artifact requirements.
- Verdict vocabulary.
- High-level kill tests.

## What Must Not Be Reused

- Existing candidate/control code.
- Existing cycle-specific runners.
- Expected-output tables.
- Hidden scenario generators.
- Artifact values as training targets.
- Baseline-specific thresholds except where predeclared by the contract.

## Readiness Decision

Independent reimplementation is the most appropriate next implementation step if human review authorizes further work. Cross-theory tournament is also necessary before any stronger theory claim, but an independent reimplementation should come first to reduce code-lineage and contract-authoring bias.

## Boundary

This recommendation authorizes at most a future contract-only independent reimplementation. It does not authorize Cycle 011, a general LCC agent, autonomous theory search, EGO migration, or theory support.
