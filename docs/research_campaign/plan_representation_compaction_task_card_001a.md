# Plan Representation Compaction Task Card 001A

Task id: `RESEARCH-CAMPAIGN-PLAN-REPRESENTATION-COMPACTION-001A`

Opened at: `2026-06-18T07:17:38.8582536-05:00`

## Problem Definition

`docs/research_campaign/plan.md` has grown into a mixed control surface and
historical ledger. Current readback shows 1223 lines, duplicate prior task
cards, and stale tail-level next-action text that conflicts with the current
scorecard frontier.

The task is to compact `plan.md` into a short campaign controller while
preserving the full pre-compaction plan text and section inventory in an
append-only appendix.

## Current Stage / Layer

Stage: campaign governance representation repair.

Layer: engineering implementation + mechanism-hypothesis governance.

This is not a mechanism experiment, Phase 3 search, candidate implementation,
runtime integration, EGO mainline change, or program terminal verdict.

## Mainline Target

Campaign documentation and ledger state only:

- `docs/research_campaign/plan.md`
- `docs/research_campaign/plan_appendix_historical_task_cards_001a.md`
- `docs/OVERALL_PROGRESS.md`
- `artifacts/research_campaign/stage_scorecard.json`
- `artifacts/research_campaign/experiment_log.jsonl`
- `artifacts/research_campaign/plan_representation_compaction_validation_001a.json`

## Enabled-State Requirement

No runtime, harness, candidate mechanism, Phase 3, route tournament, EGO
mainline, push, tag, commit, or remote anchor becomes enabled.

## Real-Trigger Evidence Requirement

The task must record:

- repo root, branch, and HEAD readback;
- current dirty status;
- original `plan.md` line count and SHA-256;
- original heading inventory;
- compacted `plan.md` line count and SHA-256;
- appendix SHA-256;
- current campaign frontier from scorecard/progress.

## Hypothesis

A representation-first split can reduce the active controller surface while
preserving all historical task cards and failures by hash-addressed appendix.

## Strongest Baseline

Baseline: keep `plan.md` as-is. This preserves all text but keeps the active
state hard to audit and allows stale next-action text to remain near the end.

Invalid shortcut baseline: delete older sections without a full append-only
snapshot. That is forbidden because it can erase failures and prior constraints.

## Ablation Requirement

Focused validation must compare pre/post:

- line count reduction for `plan.md`;
- required active fields still present;
- full pre-compaction text preserved in the appendix;
- original section headings preserved in the appendix;
- no mechanism pass or program completion claim introduced.

## Trace / Replay Requirement

The validation artifact must allow replaying the compaction by recording the
pre-compaction plan SHA-256, compact plan SHA-256, appendix SHA-256, moved/full
snapshot status, heading inventory, and source paths.

## Computed-Evidence Provenance Gate

All hashes, line counts, JSON parse checks, JSONL parse checks, and forbidden
scope checks must come from callable PowerShell computation, not handwritten
claims.

## Acceptance Gate

Pass only if:

- `plan.md` becomes a compact controller and remains parseable as markdown text;
- appendix contains the full pre-compaction plan snapshot;
- `stage_scorecard.json` parses and contains a `plan_representation` pointer;
- `experiment_log.jsonl` parses line by line;
- `OVERALL_PROGRESS.md` records the compaction without changing terminal status;
- validation artifact parses and records all required checks;
- no new `src/` or `tests/` files are introduced by this task;
- no candidate mechanism, Phase 3, route tournament, runtime/EGO mainline, push,
  tag, commit, or remote anchor is run.

## Claim Ceiling

Plan representation compaction and campaign-state hygiene only. This does not
prove mechanism validity, subjectivity, consciousness, real emotion, autonomy,
EGO readiness, companion readiness, mainline effect, route exhaustion, candidate
validation, or program completion.

## Stop Condition

Stop and report blocked if:

- current campaign frontier cannot be recovered from scorecard/progress;
- pre-compaction plan cannot be preserved by hash in the appendix;
- JSON/JSONL parsing fails after edits;
- validation finds a new source/test change introduced by this task;
- any scope would require mechanism execution or remote anchoring.

## Rollback Plan

Restore `docs/research_campaign/plan.md` from the appendix full snapshot whose
SHA-256 matches the recorded pre-compaction plan hash. Leave the failed
compaction ledger entry and validation failure preserved.

## Expected Changed Files

- `docs/research_campaign/plan_representation_compaction_task_card_001a.md`
- `docs/research_campaign/plan.md`
- `docs/research_campaign/plan_appendix_historical_task_cards_001a.md`
- `docs/OVERALL_PROGRESS.md`
- `artifacts/research_campaign/stage_scorecard.json`
- `artifacts/research_campaign/experiment_log.jsonl`
- `artifacts/research_campaign/plan_representation_compaction_validation_001a.json`

## Forbidden Changes

- `src/`
- `tests/`
- EGO runtime or mainline integration
- UI / companion behavior
- LLM integration or external services
- candidate mechanism implementation
- Phase 3 opening
- route tournament
- push, tag, commit, or remote anchor
- rewriting prior failures into passes

Auto-Remote-Anchor: forbidden
