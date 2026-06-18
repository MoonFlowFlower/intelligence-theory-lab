# Goal Stage Audit Loop Representation Compaction Task Card 001A

Task id: `RESEARCH-CAMPAIGN-GOAL-STAGE-AUDIT-LOOP-REPRESENTATION-COMPACTION-001A`

Opened at: `2026-06-18T07:51:24.4089676-05:00`

## Problem Definition

`docs/research_campaign/goal_stage_audit_loop_001a.md` is a standing campaign
governance card, but it currently mixes durable execution rules with historical
task-card acceptance text and a stale Phase 1/Hegel immediate next action.

The task is to compact it into a stable governance contract and move the full
pre-compaction text into an appendix without deleting prior constraints.

## Current Stage / Layer

Stage: campaign governance representation repair.

Layer: engineering implementation + mechanism-hypothesis governance.

This task is not a mechanism experiment, Phase 3 search, candidate
implementation, harness execution, runtime integration, EGO mainline change, or
program terminal verdict.

## Mainline Target

Campaign governance documentation and ledger state only:

- `docs/research_campaign/goal_stage_audit_loop_001a.md`
- `docs/research_campaign/goal_stage_audit_loop_001a_historical_appendix.md`
- `docs/research_campaign/plan.md`
- `docs/OVERALL_PROGRESS.md`
- `artifacts/research_campaign/stage_scorecard.json`
- `artifacts/research_campaign/experiment_log.jsonl`
- `artifacts/research_campaign/goal_stage_audit_loop_representation_compaction_validation_001a.json`

## Enabled-State Requirement

No runtime, harness execution, candidate mechanism, Phase 3, route tournament,
EGO mainline, push, tag, commit, or remote anchor becomes enabled.

## Real-Trigger Evidence Requirement

The task must record:

- repo root, branch, HEAD, and dirty-state readback;
- original card line count, SHA-256, and heading inventory;
- compact card line count and SHA-256;
- appendix SHA-256 and snapshot line count;
- current campaign frontier from `stage_scorecard.json`;
- explicit preservation of stale/historical next-action text in the appendix.

## Hypothesis

A stable governance contract with an explicit execution discipline will reduce
future model drift better than a long task-card transcript that mixes permanent
rules with stale phase-local history.

## Strongest Baseline

Baseline: keep the 520-line card as-is. This preserves all text but leaves a
stale Phase 1 next action inside a standing controller, increasing resume-time
conflict risk.

Invalid shortcut baseline: delete the historical body without an append-only
snapshot. That is forbidden.

## Ablation Requirement

Focused validation must compare pre/post:

- compact card remains under 300 lines;
- required governance sections remain present;
- appendix preserves the full pre-compaction text at text/line level;
- stale Phase 1/Hegel next action is absent from compact contract and present
  in appendix;
- the compact contract points model execution to `plan.md` for live frontier;
- no mechanism pass or program completion claim is introduced.

## Trace / Replay Requirement

The validation artifact must allow replaying the compaction by recording
pre-compaction card SHA-256, compact card SHA-256, appendix SHA-256, line
counts, heading inventory, and source paths.

## Computed-Evidence Provenance Gate

All hashes, line counts, JSON parse checks, JSONL parse checks, stale-text
checks, and forbidden-scope checks must come from callable PowerShell
computation, not handwritten claims.

## Acceptance Gate

Pass only if:

- compact governance card contains an explicit `Model Execution Discipline`
  section;
- compact governance card says live frontier belongs in `plan.md`, not this
  contract;
- stale Phase 1/Hegel immediate next action is not in compact card;
- appendix contains the full pre-compaction card snapshot;
- `stage_scorecard.json` parses and contains `goal_card_representation`;
- `experiment_log.jsonl` parses line by line;
- `OVERALL_PROGRESS.md` records the compaction without changing terminal status;
- no tracked `src/` or `tests/` diff is introduced by this task;
- no candidate mechanism, harness execution, Phase 3, route tournament,
  runtime/EGO mainline, push, tag, commit, or remote anchor is run.

## Claim Ceiling

Goal-card representation compaction and execution-discipline hardening only.
This does not prove mechanism validity, subjectivity, consciousness, real
emotion, autonomy, EGO readiness, companion readiness, mainline effect, route
exhaustion, candidate validation, or program completion.

## Stop Condition

Stop and report blocked if:

- current campaign frontier cannot be recovered from scorecard/progress;
- pre-compaction card cannot be preserved in the appendix;
- JSON/JSONL parsing fails after edits;
- validation finds a new tracked source/test change introduced by this task;
- compact card still contains stale Phase 1/Hegel immediate next-action text;
- any scope would require mechanism execution or remote anchoring.

## Rollback Plan

Restore `docs/research_campaign/goal_stage_audit_loop_001a.md` from the
appendix full snapshot. Preserve failed compaction ledger and validation
artifacts as negative bookkeeping evidence.

## Expected Changed Files

- `docs/research_campaign/goal_stage_audit_loop_representation_compaction_task_card_001a.md`
- `docs/research_campaign/goal_stage_audit_loop_001a.md`
- `docs/research_campaign/goal_stage_audit_loop_001a_historical_appendix.md`
- `docs/research_campaign/plan.md`
- `docs/OVERALL_PROGRESS.md`
- `artifacts/research_campaign/stage_scorecard.json`
- `artifacts/research_campaign/experiment_log.jsonl`
- `artifacts/research_campaign/goal_stage_audit_loop_representation_compaction_validation_001a.json`

## Forbidden Changes

- `src/`
- `tests/`
- `AGENTS.md`
- EGO runtime or mainline integration
- UI / companion behavior
- LLM integration or external services
- harness execution
- candidate mechanism implementation
- Phase 3 opening
- route tournament
- push, tag, commit, or remote anchor
- rewriting prior failures into passes

Auto-Remote-Anchor: forbidden
