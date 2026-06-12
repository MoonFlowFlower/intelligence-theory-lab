# EVIDENCE-HARNESS-CANONICAL-CONTRACT-001A

## Task ID

`EVIDENCE-HARNESS-CANONICAL-CONTRACT-001A`

## Mode

Canonical evidence-harness contract drafting only.

## Problem Definition

Cross-gate triage found a system-level evidence-harness risk: previous
score-bearing tasks may have allowed false-pass evidence through pass-shaped
artifacts, static score fields, weak baselines, non-causal metrics, replay
shortcuts, weak leakage scans, and tests that assert pass outputs.

This task creates a canonical evidence-harness contract for future Gate repairs,
deep audits, and mechanism-adjacent executable tasks.

## Current Stage

Governance contract creation. No Gate repair or execution is authorized.

## Layer

Engineering implementation layer: evidence-governance contract and artifact
schema package.

## Hypothesis

A single canonical evidence contract will reduce false-pass propagation by
making downstream admissibility depend on computed provenance, fair baselines,
real ablations, replay recomputation, leakage positive controls, and tests that
can fail for the right reasons.

This task does not prove that hypothesis. It only defines the contract.

## Baseline

Current ad hoc per-task evidence style observed by cross-gate triage:

- pass-shaped JSON
- static score fields
- weak or unfair baselines
- replay by stored hashes, stored actions, or stored verdicts
- ablation labels without real intervention
- leakage scans with broad whitelist behavior
- tests asserting pass strings, artifact existence, or perfect scores

## Ablation

No experiment ablation is executed in this task. The contract defines required
future ablation integrity rules: real interventions, rerun affected episodes,
pre/post state differences, raw scores, unclipped degradation, and causal
degradation classification.

## Trace / Replay Requirement

No mechanism trace or replay is executed in this task. The contract defines
future replay recomputation requirements: recompute behavior from serialized
state, observation, allowed context, and deterministic seed when applicable.

Hash chains may support replay but cannot replace recomputation.

## Acceptance Gate

This task passes only if:

- starting HEAD equals `7557beccbe5b89b919c61838b6688765d723fd7f`
- worktree is clean before generation
- no old artifacts, tests, or verdicts are modified
- only new contract docs and new contract artifacts are created or modified
- all required contract sections are present
- all required JSON artifacts parse
- downstream entry remains blocked
- Gate4 001C remains unauthorized
- Gate5, admission, runtime, and bridge remain unauthorized
- known Gate4 001B false-pass patterns are explicitly rejected
- final report does not claim Gate validity or mechanism validity

## Claim Ceiling

`bounded canonical evidence-harness contract only`

## Stop Condition

Stop and report blocked if:

- starting HEAD mismatches
- worktree is dirty before generation
- the task requires repairing a Gate
- the task requires modifying old artifacts, tests, or verdicts
- the task requires using provisional Gate4 001C as canonical evidence
- cross-gate triage and amendment artifacts cannot be located
- the contract would authorize downstream entry
- the contract would claim mechanism validity

## Rollback Plan

Rollback is additive and scoped:

- remove `docs/evidence_harness/EVIDENCE-HARNESS-CANONICAL-CONTRACT-001A.md`
- remove `docs/codex/tasks/EVIDENCE-HARNESS-CANONICAL-CONTRACT-001A.md`
- remove `artifacts/evidence_harness_canonical_contract_001a/`
- leave all historical artifacts, tests, and verdicts unchanged

## Downstream Authorization

- `downstream_entry_authorized`: false
- `gate4_001c_authorized`: false
- `gate5_authorized`: false
- `admission_authorized`: false
- `runtime_authorized`: false
- `bridge_authorized`: false

## What This Cannot Prove

This task cannot prove Gate validity, mechanism validity, theory validity,
architecture correctness, Gate4 001C readiness, Gate5 readiness, admission
readiness, runtime readiness, bridge readiness, EGO-mainline readiness,
consciousness, subjectivity, real autonomy, real emotion, or self-awareness.
