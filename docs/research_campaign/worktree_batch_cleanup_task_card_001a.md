# Worktree Batch Cleanup Task Card 001A

Task id: `RESEARCH-CAMPAIGN-WORKTREE-BATCH-CLEANUP-001A`

Opened: 2026-06-18

## Problem Definition

The repository contains many dirty and untracked research-campaign files from
prior bounded work. Future campaign tasks need a clean, recoverable workspace,
but evidence-like artifacts must not be hidden by broad ignore rules or staged
with an unreviewed `git add -A`.

## Current Stage And Layer

Stage: campaign repository hygiene and governance hardening.

Layer: engineering implementation + mechanism-hypothesis governance.

Mainline target: none.

Enabled-state requirement: local repository bookkeeping only.

Real-trigger evidence requirement: current `git status --short --branch`,
diff/readback of changed files, focused JSON/JSONL parse, focused harness tests,
and final clean `git status --short --branch`.

## Hypothesis

Classifying the dirty set into exact durable batches and committing those
batches locally will reduce future false-resume risk without upgrading any
mechanism claim.

## Strongest Baseline

Do nothing and rely on future models to infer the dirty state. This baseline is
weaker because untracked artifacts can be missed, overwritten, or mistaken for
fresh output.

## Invalidating Reason

If any path is unclassified, if evidence-like artifacts are ignored, if staged
sets include unrelated files, or if validation is skipped, the cleanup would be
progress theater rather than evidence hygiene.

## Baseline And Ablation Requirement

Baseline: read the complete dirty set before staging.

Ablation: leave no non-ignored dirty path unclassified; any uncommitted carry
forward must be explicitly recorded as a blocker with owner and reason.

## Trace / Replay Requirement

Record staged batches, commit commands, validation commands, final status, and
any ignore decision in the final readback. Use exact path staging only.

## Computed-Evidence Provenance Gate

Required checks:

- parse `artifacts/research_campaign/stage_scorecard.json`;
- parse every line of `artifacts/research_campaign/experiment_log.jsonl`;
- run focused tests for `tests/baseline_first_harness_001a/`;
- run focused tests for `tests/phase2b_candidate_free_headroom_001a/`;
- inspect final `git status --short --branch`.

## Planned Batches

1. Governance and campaign ledger batch:
   `AGENTS.md`, `docs/OVERALL_PROGRESS.md`, `docs/research/`,
   `docs/research_campaign/`, and `artifacts/research_campaign/`.
2. Baseline-first Phase 2 harness batch:
   `src/baseline_first_harness_001a/`,
   `tests/baseline_first_harness_001a/`, and
   `artifacts/baseline_first_harness_001a/`.
3. Phase2B candidate-free headroom harness batch:
   `src/phase2b_candidate_free_headroom_001a/`,
   `tests/phase2b_candidate_free_headroom_001a/`, and
   `artifacts/phase2b_candidate_free_headroom_001a/`.

## Ignore Policy

Existing ignored cache and log paths may remain ignored. Do not add ignore
rules for evidence-like artifacts, source, tests, task cards, audit artifacts,
or campaign ledger files. Add a new ignore rule only for classified temporary
noise that is safe to hide and not evidence-bearing.

## Acceptance Gate

- Task card exists before staging.
- Goal controller requires task-end worktree hygiene.
- All non-ignored dirty paths are classified into committed batches or explicit
  blockers.
- Staged sets are verified before each commit.
- Focused JSON/JSONL and harness checks pass or failures are recorded.
- Final `git status --short --branch` has no non-ignored dirty paths.
- No push, tag, remote anchor, EGO runtime, UI, external service, or mechanism
  candidate execution occurs.

## Claim Ceiling

Repository hygiene, local commit organization, and governance hardening only.
This task does not prove mechanism validity, learning/adaptation, self
awareness, subjective experience, real emotion, autonomy, electronic life, EGO
readiness, companion readiness, mainline effect, route exhaustion, or program
completion.

## Stop Condition

Stop and report if validation fails, if an evidence-like path cannot be
classified, if staged paths do not match the planned batch, if a secret appears,
if a commit would require rewriting history, or if final cleanup would require
deleting unowned user work.

## Rollback Plan

Do not reset or discard user work. If a local cleanup commit is later judged
wrong, revert that commit with a new explicit revert commit after user
authorization.

## Expected Changed Files

- `docs/research_campaign/worktree_batch_cleanup_task_card_001a.md`
- `docs/research_campaign/goal_stage_audit_loop_001a.md`
- `docs/research_campaign/plan.md`
- `docs/OVERALL_PROGRESS.md`
- `artifacts/research_campaign/stage_scorecard.json`
- `artifacts/research_campaign/experiment_log.jsonl`
- `artifacts/research_campaign/worktree_batch_cleanup_validation_001a.json`

Plus exact staged batches listed above.

## Forbidden Changes

- `git add -A`
- deleting or ignoring evidence-like artifacts
- rewriting historical evidence
- modifying EGO runtime or UI paths
- push, tag, remote anchor
- claiming program completion or mechanism evidence

Auto-Remote-Anchor: forbidden.
