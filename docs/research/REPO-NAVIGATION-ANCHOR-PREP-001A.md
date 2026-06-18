# REPO-NAVIGATION-ANCHOR-PREP-001A

Status: docs-only reconciliation executed; commit and conditional
remote-anchor status must come from fresh git/remote readback.

This is a docs-only reconciliation and anchor-prep task card. It authorizes
reconciliation only after explicit user execution instruction. It does not
authorize source, test, Gate, candidate, or mechanism work.

## Source Readback At Card Opening

- Repo root: `D:/Project/AIProject/MyProject/intelligence-theory-lab`. Source:
  `git rev-parse --show-toplevel`.
- Branch: `codex/meta-theory-scaffold`. Source: `git branch --show-current`.
- HEAD: `4f3dd9408077846b1b075b28c6e851ef6546630d`. Source:
  `git rev-parse HEAD`.
- Ahead/behind relative to `origin/codex/meta-theory-scaffold`: `0 0`.
  Source: `git rev-list --left-right --count
  HEAD...origin/codex/meta-theory-scaffold`.
- Dirty state at card opening:
  `docs/CURRENT_STATE.md` modified; untracked `artifacts/INDEX.json`,
  `artifacts/repo_navigation_index_001a/source_readback.json`,
  `docs/REPO_LAYOUT.md`, `docs/research/INDEX.md`,
  `docs/research/SESSION-HANDOFF-002A-current-front-and-queue.md`, and this
  task-card path after creation. Source: `git status --branch --short`;
  `git diff --name-status`; `git ls-files -o --exclude-standard`.
- Files read for this card:
  `README.md`, `AGENTS.md`, `docs/decision_log.md`,
  `docs/CURRENT_STATE.md`, `docs/research/INDEX.md`,
  `docs/REPO_LAYOUT.md`,
  `docs/research/SESSION-HANDOFF-002A-current-front-and-queue.md`,
  `artifacts/INDEX.json`,
  `artifacts/repo_navigation_index_001a/source_readback.json`.

## Problem Definition

`REPO-NAVIGATION-INDEX-001A` produced navigation outputs, but the repo remains
dirty and therefore cannot be remote-anchored. The blocking state is not code
disorder. It is docs/evidence-navigation recoverability: a pre-existing
untracked handoff file names `TLGP-001A` as the current front and includes older
remote-anchor instructions, while tracked campaign files and the new navigation
readback preserve a frontier conflict as `unknown`. Source:
`docs/CURRENT_STATE.md`;
`docs/research/SESSION-HANDOFF-002A-current-front-and-queue.md`;
`docs/research_campaign/plan.md`; `docs/OVERALL_PROGRESS.md`.

## Current Stage / Layer

Engineering-governance / repository information architecture only. This task is
not a Gate, mechanism experiment, admission route, bridge route, runtime route,
candidate implementation, source repair, or test repair. Source: `AGENTS.md`;
`docs/CURRENT_STATE.md`.

## Mainline Target

None. No EGO mainline, runtime, bridge, Gate implementation, candidate
implementation, `src/`, `tests/`, or live entrypoint is targeted. Source:
`AGENTS.md`; `README.md`.

## Enabled-State Requirement

Documentation only. Any execution of this card may make navigation documents and
machine-readable readback easier to recover, but must not enable a runtime path,
Gate path, admission path, bridge path, source path, or test path. Source:
`AGENTS.md`; `docs/REPO_LAYOUT.md`.

## Real-Trigger Evidence Requirement

The only valid trigger evidence is current repo/tool readback: git status,
branch, HEAD, ahead/behind, exact dirty paths, exact staged set if staging is
authorized, file hashes or path reads for the navigation and handoff files, and
remote/tag readback only if conditional anchoring later becomes authorized and
all gates pass. Source: `AGENTS.md`;
`artifacts/repo_navigation_index_001a/source_readback.json`.

## Real Objective

Prepare a clean, auditable docs-only boundary for the navigation-index work by
classifying or repairing the handoff conflict without moving, deleting,
renaming, or reinterpreting evidence, and without upgrading any route claim.

## Hypothesis

If the handoff conflict is explicitly classified, navigation files cite their
sources, and a new source-readback artifact records the exact dirty/staged
state, then a later exact-path docs-only commit can produce a clean anchorable
boundary. This would improve canonical-state recoverability only.

## Strongest Baseline Explanation

The apparent anchor problem may be only local working-tree residue: navigation
outputs are uncommitted, and the handoff contains stale or session-specific
remote-anchor instructions. No mechanism, route, Gate, or source change may be
needed. Source: `git status --branch --short`;
`docs/research/SESSION-HANDOFF-002A-current-front-and-queue.md`.

## Strongest Reason This Task May Be Invalid

The handoff may require decisions outside docs-only reconciliation, such as
banking `TLGP-001A`, validating its mechanism result, adding a cross-episode
meta-learner panel, touching `src/` or `tests/`, or anchoring TLGP artifacts as
a provisional experiment boundary. If so, this task must stop rather than
expand scope. Source:
`docs/research/SESSION-HANDOFF-002A-current-front-and-queue.md`;
`artifacts/TLGP-001A/LIMITATIONS.txt`; `AGENTS.md`.

## Falsifier For The Framing

The docs-only framing is false if clean anchor preparation requires any of:
deciding new mechanism route validity, upgrading `TLGP-001A` beyond its
limitations, editing `src/**`, editing `tests/**`, changing scripts or remote
configuration, deleting artifacts, moving evidence paths, or running/repairing
a Gate/harness/test/source path.

## Evidence That Would Still Be Insufficient

Handoff prose, artifact `passed` fields, old anchor instructions, and clean
Markdown alone are insufficient. The task needs fresh git/file readback and, if
any commit is made later, exact staged-path evidence and post-commit clean
worktree evidence. Source: `AGENTS.md`; `docs/REPO_LAYOUT.md`.

## Collision Record

### Candidate 1: Block-Preserving Readback Only

- What it would produce: a new anchor-prep readback that labels the handoff as a
  remaining blocker and performs no commit or remote action.
- Strongest cheap baseline: status reporting alone can match it.
- Leakage / hard-coding risk: low; risk is a report-shaped non-action.
- Smallest falsifying test: `git status --branch --short` still shows dirty
  non-navigation paths after the readback, so anchor remains blocked.
- Expected failure mode: it preserves truth but does not make the repo
  anchorable.

### Candidate 2: Docs-Only Reconciliation And Anchor Prep

- What it would produce: classify or repair the handoff conflict, update
  navigation docs only if needed, create
  `artifacts/repo_navigation_anchor_prep_001a/source_readback.json`, verify
  exact path scope, and prepare for a later exact-path commit.
- Strongest cheap baseline: this may merely reconcile stale local docs rather
  than increase evidence strength.
- Leakage / hard-coding risk: medium; risk is silently turning handoff prose
  into stronger route status.
- Smallest falsifying test: any edited status claim lacks a source path, any
  route status is upgraded, or any `src/**`, `tests/**`, `scripts/**`, remote
  config, or existing evidence path changes.
- Expected failure mode: unresolved handoff conflict remains and anchor stays
  blocked.

### Candidate 3: Full TLGP Anchor Recovery

- What it would produce: anchor TLGP source/tests/artifacts and the handoff as a
  provisional experiment boundary.
- Strongest cheap baseline: this is outside docs-only and would mix mechanism
  evidence with navigation cleanup.
- Leakage / hard-coding risk: high; it could over-read or bank a provisional
  result that still requires independent audit and a cross-episode meta-learner
  panel.
- Smallest falsifying test: required change list includes `src/**`, `tests/**`,
  or TLGP artifact/source validation.
- Expected failure mode: scope expansion into mechanism evidence or provisional
  experiment anchoring.

Selected approach for execution, if separately authorized: Candidate 2, with an
immediate downgrade to Candidate 1 if the handoff cannot be reconciled within
docs-only scope. Candidate 3 is explicitly rejected for this task.

## Baseline Requirement

No mechanism baseline is authorized. The governance baseline is the no-op dirty
state recorded by git readback. Any execution must show whether the docs-only
reconciliation changed anchor readiness relative to that baseline.

## Ablation Requirement

No mechanism ablation is authorized. The governance ablation is: without
classifying or repairing the handoff conflict, auto-anchor remains blocked by a
dirty or unauthorized scope.

## Trace / Replay Requirement

No mechanism trace/replay is authorized. The required replayable evidence is a
machine-readable source-readback JSON containing files read, command readback,
allowed paths, forbidden paths, staged paths if any, final status, and any
remaining blockers.

## Computed-Evidence Provenance Gate

No score, verdict, Gate result, candidate result, baseline metric, ablation
metric, replay metric, or mechanism evidence may be introduced. The only
computed/readback evidence is callable local repo readback from git and file
hash/path reads. Static prose must not be used to claim anchor readiness.

## Allowed Files For Later Execution

Execution may create or modify only the following paths:

- `docs/research/REPO-NAVIGATION-ANCHOR-PREP-001A.md`
- `docs/CURRENT_STATE.md`
- `docs/research/INDEX.md`
- `docs/REPO_LAYOUT.md`
- `docs/research/SESSION-HANDOFF-002A-current-front-and-queue.md`
- `artifacts/INDEX.json`
- `artifacts/repo_navigation_index_001a/source_readback.json`
- `artifacts/repo_navigation_anchor_prep_001a/source_readback.json`

The previous navigation output paths may be staged unchanged if a later
execution commits the navigation boundary, but existing experiment evidence
under `artifacts/**` outside the listed paths is read-only.

## Forbidden Changes

- `src/**`
- `tests/**`
- `scripts/**`
- `AGENTS.md` except read-only citation
- `README.md` except read-only citation
- existing evidence artifacts outside the listed navigation readback paths
- deleting, moving, renaming, compressing, or rewriting evidence paths
- changing remote config, credential files, push helpers, tokens, or ignored
  local-only files
- running or repairing Gate, admission, bridge, harness, candidate, source, or
  test logic
- upgrading `TLGP-001A` or any route status beyond what cited source files say

## Required Readback For Later Execution

Execution must read and record:

- `README.md`
- `AGENTS.md`
- `docs/decision_log.md`
- `docs/CURRENT_STATE.md`
- `docs/research/INDEX.md`
- `docs/REPO_LAYOUT.md`
- `docs/research/SESSION-HANDOFF-002A-current-front-and-queue.md`
- `docs/research_campaign/plan.md`
- `docs/OVERALL_PROGRESS.md`
- `artifacts/INDEX.json`
- `artifacts/repo_navigation_index_001a/source_readback.json`
- representative `TLGP-001A` limitation/result/provenance files only as
  read-only source citations if the handoff text is reconciled

Execution must also record current branch, HEAD, ahead/behind, dirty paths,
untracked paths, cached diff, final diff, and exact staged paths if staging is
authorized.

## Acceptance Gate

- No existing evidence path is moved, renamed, deleted, compressed, or
  rewritten.
- Every status claim in edited docs cites an existing repo file path.
- Every route status in `docs/research/INDEX.md` remains one of: `active`,
  `closed`, `downgraded`, `blocked`, `superseded`, `unknown`.
- Claim ceiling remains repo navigation / anchor-prep only.
- Mainline integration remains none.
- Enabled status remains documentation only.
- Real trigger evidence is source readback of existing repo files and git
  readback only.
- The handoff conflict is either:
  - reconciled within docs-only scope and included in the allowed staged set; or
  - preserved as a named blocker, with no commit/anchor claim.
- If a later execution commits, staging uses exact allowed paths only. No
  `git add -A`.
- If a later execution commits, post-commit worktree and index must be clean
  before any conditional remote-anchor step.
- If any unauthorized path appears in staged or unstaged changes, stop.

## Stop Condition

Stop if the task requires deciding new mechanism route validity, changing any
Gate/harness/test/source code, deleting artifacts, moving source-readback
targets, upgrading a claim, resolving `TLGP-001A` limitations, running a
cross-episode meta-learner, repairing or using push scripts, changing remote
configuration, rebasing/resetting/amending for push, or exposing credentials.

## Rollback Plan

Before any commit, delete only files created for this task and revert only edits
made by this task. Do not delete or alter prior navigation outputs or the
pre-existing handoff unless a later execution explicitly modified them and needs
to roll back that exact modification. After any future remote anchor, do not
rewrite remote history; use a new bounded corrective task and commit.

## Auto-Remote-Anchor Decision

Auto-Remote-Anchor: conditional.

Opening this card does not authorize staging, committing, pushing, tagging, or
remote-anchor. Conditional auto-anchor may be executed only after a separate
explicit user instruction to execute this task card and only if all acceptance
gates above pass.

If conditional anchor is later reached, use a lightweight tag named:

`remote-anchor-repo-navigation-anchor-prep-001a-<short-head>`

The required readback is: local HEAD full hash, remote branch full hash, local
tag full hash, remote tag full hash, exact match yes/no, local tag type, final
ahead/behind, final `git status --branch --short`, and final
`git diff --name-status`.

## Claim Ceiling

Repository navigation reconciliation and anchor preparation only. No mechanism
evidence, no Gate pass, no candidate feasibility, no baseline result, no
ablation result, no replay result, no mainline effect, no route validity, no
program completion, no agency, no autonomy, no consciousness, no subjective
experience, no real emotion, no EGO readiness, no runtime readiness, no
companion readiness, and no user-benefit claim.

## Next Minimal Closed-Loop Action

If the user explicitly authorizes execution, perform a fresh readback, create
`artifacts/repo_navigation_anchor_prep_001a/source_readback.json`, reconcile or
block the handoff conflict within the allowed paths, verify exact scope, and
only then decide whether a docs-only commit is allowed.
