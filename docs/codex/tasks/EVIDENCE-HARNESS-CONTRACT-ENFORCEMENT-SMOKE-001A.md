# EVIDENCE-HARNESS-CONTRACT-ENFORCEMENT-SMOKE-001A

## Task ID

`EVIDENCE-HARNESS-CONTRACT-ENFORCEMENT-SMOKE-001A`

## Mode

Minimal executable evidence-harness contract enforcement smoke only.

This is not a Gate repair, Gate execution, mechanism validation, Gate4 001C
continuation, Gate5, admission, runtime, or bridge task.

## Problem Definition

The canonical evidence-harness contract is anchored, but a contract alone does
not reject future pass-shaped evidence. This task adds a minimal callable
enforcer that rejects known false-pass evidence-pattern features and verifies
that rejection is not based only on a task-id or commit denylist.

## Current Stage

Executable smoke over the evidence-harness contract. The output is a bounded
enforcement-path check, not Gate validity evidence.

## Layer

Engineering implementation layer: executable enforcement smoke over evidence
admissibility rules.

## Hypothesis

If the canonical contract is useful, a minimal callable enforcer should reject
the known Gate4 001B false-pass boundary and synthetic positive-control
false-pass fixtures through detected evidence-pattern features.

This task does not prove the contract is complete.

## Baseline

Baseline failure mode: a future Gate repair emits contract-shaped artifacts,
pass-shaped result fields, static perfect scores, label-only ablations, clean
leakage literals, replay pass strings, and tests that assert pass outputs, while
no executable rejection path detects the false-pass pattern.

## Ablation

No mechanism ablation is run. The smoke includes a synthetic false-pass fixture
with label-driven ablation and clipped/perfect score surfaces to verify the
enforcer rejection path.

## Trace / Replay Requirement

No mechanism replay is run. The smoke scans replay evidence surfaces for stored
action, stored verdict, hash-only, or pass-string replay shortcuts.

## Acceptance Gate

This task passes only if:

- starting HEAD equals `b11424652c791fd9153322db77d959c3c0cdacac`
- worktree is clean before generation
- old artifacts, tests, and verdicts are not modified
- provisional Gate4 001C is not used
- the enforcer is callable from code
- the enforcer detects the synthetic positive-control false-pass fixture
- Gate4 001B is not classified as admissible downstream evidence
- rejection is not based only on task-id or commit denylist
- one governance-anchor scope control classifies differently from false-pass
  fixtures
- tests invoke the enforcer path
- all JSON artifacts parse
- downstream authorization fields remain false

## Claim Ceiling

`bounded evidence-harness contract enforcement smoke only`

## Stop Condition

Stop and report blocked if the start state mismatches, the worktree is dirty
before generation, old Gate artifacts/tests/verdicts must be modified, any Gate
must be repaired, provisional Gate4 001C is required, the positive control is not
detected, static denylist-only rejection is the only path, or any downstream
authorization would become true.

## Rollback Plan

Remove only:

- `docs/codex/tasks/EVIDENCE-HARNESS-CONTRACT-ENFORCEMENT-SMOKE-001A.md`
- `src/evidence_harness_contract_enforcement_smoke_001a/`
- `tests/test_evidence_harness_contract_enforcement_smoke_001a.py`
- `artifacts/evidence_harness_contract_enforcement_smoke_001a/`

Historical artifacts, tests, and verdicts remain unchanged.

## Downstream Authorization

- `downstream_entry_authorized`: false
- `gate4_001c_authorized`: false
- `gate5_authorized`: false
- `admission_authorized`: false
- `runtime_authorized`: false
- `bridge_authorized`: false

## What This Cannot Prove

This smoke does not prove Gate validity, mechanism validity, theory validity,
architecture correctness, Gate4 001C authorization, Gate5 authorization,
admission authorization, runtime authorization, bridge authorization,
EGO-mainline readiness, agency, selfhood, consciousness, emotion, relationship
learning, or stable user benefit.
