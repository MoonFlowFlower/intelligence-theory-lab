# Stage Audit Loop Governance Contract 001A

Task id: `RESEARCH-CAMPAIGN-GOAL-STAGE-AUDIT-LOOP-001A`

Last updated: 2026-06-18T07:55:29.5783534-05:00

Historical appendix: `docs/research_campaign/goal_stage_audit_loop_001a_historical_appendix.md`

Pre-compaction card SHA-256: `793ee8c170dad4074281fb11c45ce83dec8026a751df93d23621aa20e72cca59`

Appendix SHA-256: `6ffa5e9dbc1b9bc6a79c8a8732a4ad4c40aef05a60eb9bac5df4463ef68bd41f`

## Purpose

This file is the standing governance contract for the long-running intelligence
mechanism research campaign. It defines how a model must advance phases,
record evidence, preserve failures, and enforce claim ceilings.

This file is not the live campaign controller. The live frontier, current
checkpoint, and next action belong in `docs/research_campaign/plan.md`. On
every continuation, the model must read `plan.md` before choosing work.

## Layer And Claim Ceiling

Layer: engineering implementation + mechanism-hypothesis governance.

Mainline integration status: none.

Enabled status: governance contract only.

Real trigger evidence: repository state, plan/progress/scorecard/ledger
readback, task-card clauses, validation artifacts, and reviewer audit artifacts.

Claim ceiling: phase-governance and evidence-hygiene only. This contract cannot
prove mechanism validity, self-awareness, subjective experience, real emotion,
autonomy, electronic life, EGO readiness, companion readiness, route exhaustion,
program completion, or mainline effect.

Auto-Remote-Anchor: forbidden unless a later bounded task card explicitly
authorizes it and all remote-anchor gates pass.

## Program Goal And Terminal Contract

The program goal is a long-running falsifiable campaign for bounded
functional-subject proxy mechanisms. The campaign remains `active_not_complete`
unless a terminal verdict is recorded with machine-readable evidence, reviewer
audit, and ledger/progress/scorecard agreement.

Allowed terminal verdicts:

- `program_candidate_validated_bounded`
- `program_needs_reframing`
- `program_route_exhausted_with_negative_evidence`
- `program_blocked_by_external_dependency`

Forbidden terminal verdicts and proof claims:

- `consciousness_proven`
- `real_emotion_proven`
- `electronic_life_proven`
- `self_awareness_proven`
- `autonomy_proven`
- `agi_proven`
- `ego_ready`
- `companion_ready`

Task-card creation, local validation, JSON parse success, a single phase pass,
or a chat-only reviewer/subagent response never completes the program.

## Model Execution Discipline

Every model that touches this campaign must execute this checklist in order.
Skipping a step is a stop condition, not a judgment call.

1. Read current repo state: root, branch, HEAD, upstream/ahead-behind when
   relevant, and `git status --short --branch -uall`.
2. Read live campaign state from `docs/research_campaign/plan.md`,
   `docs/OVERALL_PROGRESS.md`,
   `artifacts/research_campaign/stage_scorecard.json`, and
   `artifacts/research_campaign/experiment_log.jsonl`.
3. Identify the current layer, real objective, strongest baseline explanation,
   strongest invalidating reason, claim ceiling, stop condition, and rollback
   plan before edits or experiments.
4. Confirm a bounded task card exists. If it is missing or stale, repair the
   task card first and do not execute the experiment.
5. Before work, write expected changed files, forbidden changes, baseline,
   ablation, trace/replay, computed provenance, acceptance gate, and
   Auto-Remote-Anchor decision into the task record.
6. During work, append failures and blockers as they occur. Failed audits and
   failed validations are evidence and must not be overwritten by later passes.
7. After work, update `experiment_log.jsonl`, `stage_scorecard.json`,
   `docs/OVERALL_PROGRESS.md`, and `plan.md` before moving to the next frontier.
8. Before final response, run task-end worktree hygiene: classify every dirty or
   untracked path, commit authorized durable batches with exact path staging, or
   record an explicit carry-forward blocker. Do not leave unclassified dirty
   state.
9. Run focused validation. A validation that only asserts pass, uses static
   verdicts, or does not parse/recompute the evidence path is invalid.
10. Treat reviewer/subagent output as evidence only after it is recorded in an
   audit artifact, ledger, scorecard, and progress checkpoint.
11. If plan/progress/scorecard/ledger disagree, stop and repair the state before
    opening the next task.

## Live Frontier Rule

This contract must not store a phase-specific immediate next action. The live
frontier is always read from:

- `docs/research_campaign/plan.md`
- `docs/OVERALL_PROGRESS.md`
- `artifacts/research_campaign/stage_scorecard.json`
- the tail of `artifacts/research_campaign/experiment_log.jsonl`

If these disagree, no new phase, candidate, harness execution, route
tournament, or terminal verdict may be opened until the disagreement is
recorded and repaired.

## Task-End Worktree Hygiene

Every task must end with a repository hygiene pass before the final readback:

1. Run and report `git status --short --branch -uall`.
2. Classify every modified or untracked path as one of:
   - durable governance/progress/ledger evidence;
   - durable source, test, harness, or artifact output;
   - temporary generated noise already covered by scoped ignore rules;
   - external or user-owned carry-forward that must not be touched.
3. Commit durable batches locally when the task card or user explicitly
   authorizes commits. Use exact path staging only and verify the staged set
   before every commit.
4. Do not use `git add -A`.
5. Do not ignore evidence-like artifacts, task cards, audit records, source, or
   tests to hide work. New ignore rules are allowed only for classified
   temporary noise.
6. If committing is not authorized, record the dirty carry-forward in
   `plan.md`, `OVERALL_PROGRESS.md`, `stage_scorecard.json`, and
   `experiment_log.jsonl` as a known blocker before ending the task.
7. Preserve failed and negative evidence in the ledger. Later successful
   commits must not overwrite or delete failure records.
8. Push, tag, and remote-anchor remain forbidden unless a later bounded task
   card explicitly authorizes them and all remote-anchor gates pass.

Clean worktree is a governance condition, not a mechanism result. It cannot
upgrade any claim ceiling.

## Phase Advancement Protocol

The only valid phase loop is:

1. open or repair a bounded phase task card;
2. validate the start state;
3. execute only the authorized bounded scope;
4. record artifacts, traces, failures, and provenance immediately;
5. run focused local validation;
6. run read-only reviewer/subagent audit when required;
7. preserve every audit failure;
8. repair only the bounded failing surface;
9. re-run validation/audit;
10. open the next phase only after recorded `success_reached`.

Reviewer verdict vocabulary:

- `success_reached`
- `needs_more_implementation`
- `needs_more_exploration`
- `blocked_by_external_dependency`
- `needs_reframing`

## Evidence Requirements

Every score-bearing result must come from callable computation paths and record:

- producer function;
- input artifacts;
- run id;
- seed/context/episode ids;
- aggregation rule;
- code path hash.

Baselines must be independent callable implementations with the same input
boundary and budget as the candidate. Ablations must rerun real episodes under
interventions. Leakage scans must include positive controls. Replay must
recompute behavior from serialized state plus observation.

Unused frozen seeds, train contexts, heldout contexts, or counterfactual pairs
block the evidence claim.

## Baseline-First And No-Headroom Rule

Executable mechanism or proxy-evidence phases after formalization must run a
candidate-free baseline-first headroom battery before candidate work.

If the strongest fair baseline reaches the oracle within the equivalence band,
record no-headroom negative evidence, block candidate search and Phase 3, and
redesign the surface before candidate authoring.

After repeated no-headroom, the next valid route is problem-representation
redesign, surface-family closure, claim downgrade, or a reviewer-audited
terminal/reframing checkpoint. Do not run a route tournament to rescue the
surface.

## Required Prior-Evidence Search

Before a phase task or audit prompt, search relevant prior negative evidence,
failed validations, failed audits, baseline-equivalence records, stale-state
repairs, leakage findings, replay failures, and no-headroom artifacts.

Prior artifacts are challenge inputs, not inherited proof. Do not rewrite old
failures into passes.

## Acceptance Gates

Controller-card acceptance means only this governance contract is present,
compact, and externally recoverable. It is not program completion.

Program completion requires one allowed terminal verdict plus machine-readable
evidence, phase-chain agreement, reviewer audit, and explicit claim ceiling.

## Stop Conditions

Stop and record a blocker if any of these occur:

- live state files disagree and the disagreement is not repaired;
- a model proposes work without a bounded task card;
- an audit failure is deleted, overwritten, or summarized away;
- baseline-first evidence shows no headroom but candidate work is proposed;
- a score lacks callable provenance;
- replay, ablation, leakage, or baseline checks are static or self-reported;
- a chat-only reviewer/subagent result is treated as ledger truth;
- `src/`, `tests/`, runtime, EGO mainline, push, tag, commit, or remote anchor
  is touched without explicit authorization;
- wording upgrades evidence into consciousness, real emotion, autonomy,
  electronic life, EGO readiness, companion readiness, mechanism validity, or
  mainline effect.

## Recovery And Rollback

To recover the pre-compaction governance text, use the historical appendix:
`docs/research_campaign/goal_stage_audit_loop_001a_historical_appendix.md`.

Rollback must be explicit, bounded, and recorded. Do not delete prior Phase 0,
Phase 1, Phase 2, Phase2B, Phase2C, failed validation, failed audit, or
no-headroom evidence.

## Representation Maintenance

This contract stores durable rules only. Historical task-card body, prior
acceptance text, and stale immediate-next-action text belong in the appendix.
Live current state belongs in `plan.md` and the campaign ledger.
