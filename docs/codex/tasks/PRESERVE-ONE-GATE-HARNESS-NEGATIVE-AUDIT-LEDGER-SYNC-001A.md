# PRESERVE-ONE-GATE-HARNESS-NEGATIVE-AUDIT-LEDGER-SYNC-001A

## Problem Definition

The future-only harness negative audit was preserved locally in commit
`c27d4ffcc855876c26211407f5a9152dd0aa405f`, but remote-anchor was blocked by
two pre-existing dirty canonical ledger files modified by independent audit:

- `docs/NEGATIVE_EVIDENCE_LEDGER.md`
- `theories/failed_claims.yaml`

This task resolves the dirty state by validating and preserving or rejecting the
canonical ledger changes under a separate bounded hygiene task. It must not
modify harness source, verifier source, Gate artifacts, or mainline wiring.

## Current Stage / Layer

Engineering-governance / negative-audit ledger sync and remote-anchor hygiene
only.

## Mainline Target

None. Do not wire into Gate3, Gate4, integrated admission, bridge, runtime,
companion, or EGO mainline.

## Enabled-State Requirement

No new enabled path.

## Real-Trigger Evidence Requirement

Start from live repo readback:

- expected local HEAD:
  `c27d4ffcc855876c26211407f5a9152dd0aa405f`
- expected remote branch baseline:
  `cb95bbdb06c9fadbbbf7765ae61acc46609ed994`
- expected dirty files:
  - `docs/NEGATIVE_EVIDENCE_LEDGER.md`
  - `theories/failed_claims.yaml`

Classify the dirty files by file readback, git diff, and YAML parser
validation.

## Hypothesis

The dirty files are legitimate canonical negative-evidence ledger updates
corresponding to the `cb95bbd` harness downgrade and can be preserved in a
separate hygiene commit after validation.

## Strongest Baseline

Treat the dirty files as untrusted out-of-scope edits and revert them, leaving
only commit `c27d4ffc` as preserved negative audit.

## Ablation / Contrast

If preserving the ledger changes, record what would be lost by reverting them:

- canonical negative-evidence ledger reference
- structured failed-claim record
- global successor constraint requiring candidate-inaccessible ground truth

If reverting, preserve the rejected diff in the task artifact directory and
explain why it was not safe to commit.

## Trace / Replay Requirement

Record:

- exact start HEAD
- remote branch HEAD
- exact dirty file list
- diff summaries for both ledger files
- YAML parse result
- append-only verification result
- final HEAD
- final worktree status
- local/remote/tag hash readback if anchored

## Computed-Evidence Provenance Gate

Use git plumbing/file readback and a YAML parser. Do not rely on narrative
self-consistency.

Validation must check:

- no harness source modified
- no verifier source modified
- no Gate3/Gate4 source or artifacts modified
- no integrated admission, bridge, runtime, or mainline files modified
- markdown ledger base content is preserved
- prior structured failed-claim entries are not removed or mutated
- YAML parses
- `negative_evidence_policy.overwrite_allowed` remains false
- the new entry states a bounded claim ceiling and no readiness or mechanism
  validity claim

## Acceptance Gate

- `c27d4ffcc855876c26211407f5a9152dd0aa405f` remains an ancestor of the final
  branch head.
- Dirty ledger files are either:
  - validated and committed as a separate ledger-sync commit; or
  - reverted with a blocker/rejection artifact.
- Final worktree is clean.
- Final branch is pushed.
- Remote anchor is performed only after clean worktree.
- Local HEAD, remote branch HEAD, local tag, and remote tag exactly match.

## Claim Ceiling

Negative-audit ledger sync and remote-anchor hygiene only. No Gate validity,
mechanism validity, integrated admission readiness, mainline effect, agency,
consciousness, emotion, autonomy, stable user benefit, runtime readiness, bridge
readiness, or EGO readiness claim.

## Stop Condition

Stop if:

- either ledger file is truncated or malformed and cannot be reconstructed
  safely
- the change is not append-only
- previous negative evidence entries are removed or overwritten
- YAML fails to parse
- the task tries to repair the harness
- the task tries to apply the harness to a real Gate
- source files outside the allowed ledger/artifact/task-card scope change

## Rollback Plan

If validation fails, restore both ledger files to the committed baseline,
preserve the rejected diff in the task artifact directory, and report
`ledger_sync_blocked`. Do not remote-anchor as a successful boundary.

## Expected Changed Files

- `docs/codex/tasks/PRESERVE-ONE-GATE-HARNESS-NEGATIVE-AUDIT-LEDGER-SYNC-001A.md`
- `artifacts/one_gate_harness_negative_audit_ledger_sync_001a/**`
- `docs/NEGATIVE_EVIDENCE_LEDGER.md`
- `theories/failed_claims.yaml`

## Forbidden Changes

- `src/one_gate_future_only_non_circular_harness_001a/**`
- `src/evidence_admission_verifier_001a/**`
- Gate3/Gate4 source or artifacts except read-only references
- integrated admission / bridge / runtime / mainline files
- unrelated tests
- unrelated artifacts

## Auto-Remote-Anchor Decision

Authorized if acceptance gates pass, final worktree is clean, branch is pushed,
and local HEAD / remote branch / local tag / remote tag exactly match.

Suggested tag:
`remote-anchor-one-gate-harness-negative-audit-ledger-sync-001a-<shortsha>`.
