# Repository Layout Policy

Task id: `REPO-NAVIGATION-INDEX-001A`.

This file is a navigation and layout policy. It does not authorize moving,
renaming, deleting, rewriting, or reinterpreting existing evidence.

## Claim Ceiling

Repository navigation and canonical-state recoverability only. No mechanism
evidence, Gate pass, candidate feasibility, mainline effect, agency, autonomy,
consciousness, subjective experience, real emotion, EGO readiness, companion
readiness, route exhaustion, or program completion. Source: `AGENTS.md`;
`README.md`; `docs/CURRENT_STATE.md`.

## Top-Level Layout

- `README.md`: high-level lab purpose and non-runtime framing. Source:
  `README.md`.
- `AGENTS.md`: operating contract, claim ceilings, evidence requirements,
  task-card requirements, git/anchor rules, and forbidden runtime/product
  upgrades. Source: `AGENTS.md`.
- `docs/CURRENT_STATE.md`: current navigation readback for this repo. It is not
  evidence and must cite source files for status claims. Source:
  `docs/CURRENT_STATE.md`.
- `docs/decision_log.md`: append-style decision record for route closures,
  downgrades, and governance boundaries. Source: `docs/decision_log.md`.
- `docs/research/`: route records, task cards, audit preservations, negative
  evidence closeouts, methodology notes, and handoffs. Source:
  `docs/research/INDEX.md`; `docs/research/SESSION-HANDOFF-002A-current-front-and-queue.md`.
- `docs/research_campaign/`: compact campaign controller, phase task cards,
  campaign plan, and campaign bookkeeping. Source:
  `docs/research_campaign/plan.md`; `docs/OVERALL_PROGRESS.md`.
- `docs/codex/`: Codex task cards, audit records, and reusable governance
  contracts for Codex-executed tasks. Source: `docs/decision_log.md`.
- `artifacts/`: evidence bundles and navigation registries. Existing
  subdirectories are immutable evidence/navigation records unless a future
  bounded task explicitly authorizes a new additive artifact. Source:
  `AGENTS.md`; `artifacts/INDEX.json`.
- `artifacts/research_campaign/`: machine-readable campaign ledger, scorecard,
  validation records, and audit outputs. Source:
  `docs/research_campaign/plan.md`; `artifacts/research_campaign/stage_scorecard.json`.
- `artifacts/INDEX.json`: machine-readable navigation registry for artifact
  directories. It is metadata only and does not replace artifact evidence.
  Source: `artifacts/INDEX.json`.
- `artifacts/repo_navigation_index_001a/source_readback.json`: source-readback
  record for this navigation-index task. Source:
  `artifacts/repo_navigation_index_001a/source_readback.json`.
- `artifacts/repo_navigation_anchor_prep_001a/source_readback.json`:
  source-readback record for docs-only navigation reconciliation and
  anchor-prep. It does not replace route evidence or authorize mechanism
  claims. Source:
  `docs/research/REPO-NAVIGATION-ANCHOR-PREP-001A.md`.
- `src/` and `tests/`: implementation and test paths. This navigation task does
  not modify them. Source: `AGENTS.md`;
  `artifacts/repo_navigation_index_001a/source_readback.json`.
- Historical top-level packages such as `cmbc_companion/`,
  `predictive_action_learning_contract_001/`,
  `predictive_action_learning_contract_001c/`, and `theory_lab/` remain in
  place because docs and tests still cite them. Source: `docs/decision_log.md`;
  `artifacts/repo_navigation_index_001a/source_readback.json`.

## Evidence Preservation Rules

- Do not move, rename, delete, compress, or rewrite existing evidence paths as a
  cleanup operation. Source: `AGENTS.md`.
- Do not use `git add -A` for evidence/governance work; stage exact paths under
  the bounded task scope only. Source: `AGENTS.md`;
  `docs/research_campaign/worktree_batch_cleanup_task_card_001a.md`.
- Do not use broad ignored-file cleanup when ignored files may include
  push/token helpers or other local-only sensitive paths. Source: `.gitignore`;
  `docs/research/SESSION-HANDOFF-002A-current-front-and-queue.md`.
- New evidence-bearing work should continue using
  `artifacts/<task_id>/` with machine-readable `result.json`, trace, baseline,
  ablation, replay, failure, and claim-ceiling records when required by the task
  card. Source: `AGENTS.md`.
- Navigation artifacts such as `artifacts/INDEX.json` and
  `artifacts/repo_navigation_index_001a/source_readback.json` are not
  experiment evidence; they only point to source evidence. Source:
  `docs/CURRENT_STATE.md`.
- Handoff overlays may supersede handoff publication instructions for current
  anchor authority without changing the preserved route/evidence content.
  Source: `docs/research/SESSION-HANDOFF-002A-current-front-and-queue.md`;
  `docs/research/REPO-NAVIGATION-ANCHOR-PREP-001A.md`.

## Route Status Policy

- Every route row in `docs/research/INDEX.md` must use one of: `active`,
  `closed`, `downgraded`, `blocked`, `superseded`, or `unknown`. Source:
  `docs/research/INDEX.md`.
- Use `active` only for the current campaign/controller/navigation frontier or
  a provisional current front whose caveats are explicitly cited. Source:
  `docs/CURRENT_STATE.md`; `artifacts/TLGP-001A/LIMITATIONS.txt`.
- Use `unknown` when live source files disagree and the task is not authorized
  to reconcile them. Source: `docs/CURRENT_STATE.md`;
  `docs/research/SESSION-HANDOFF-002A-current-front-and-queue.md`;
  `docs/research_campaign/plan.md`.
- Use `closed`, `downgraded`, or `blocked` only when an existing route record or
  artifact says so. Source: `docs/research/INDEX.md`;
  `docs/decision_log.md`.

## Update Procedure

1. Read `README.md`, `AGENTS.md`, `docs/decision_log.md`,
   `docs/research_campaign/plan.md`, `docs/OVERALL_PROGRESS.md`, recent
   `docs/research/` records, and representative artifact JSON files. Source:
   `artifacts/repo_navigation_index_001a/source_readback.json`.
2. Update only navigation files unless a separate bounded task authorizes
   evidence/source/test changes. Source: `AGENTS.md`.
3. Preserve source conflicts as `unknown`; do not resolve them by inference.
   Source: `docs/CURRENT_STATE.md`.
4. Regenerate `artifacts/INDEX.json` from artifact directory readback and keep
   it as metadata only. Source: `artifacts/INDEX.json`.
5. End with git status readback and scope verification. Source:
   `artifacts/repo_navigation_index_001a/source_readback.json`.
