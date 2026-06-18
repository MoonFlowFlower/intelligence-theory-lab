# Strict Intelligence Mechanism Research Campaign Plan

Last updated: 2026-06-18T08:25:32-05:00

This file is the compact campaign controller. Historical task cards, prior
checkpoints, and the full pre-compaction plan snapshot are preserved in:

- appendix: `docs/research_campaign/plan_appendix_historical_task_cards_001a.md`
- pre-compaction plan sha256: `b960eaf54f5dd4ef33d7e6435b00491fec72a162139cd50e33c4c7a1c346b8f0`
- appendix sha256: `2cd3cb668ee8814ce46c13ea8a593e0e96c8025b31887119762c8db56128c247`
- snapshot preservation caveat: text-level snapshot preserved; final validation records a non-byte-exact trailing-whitespace caveat

## Program Goal

Build a long-running, falsifiable, recovery-safe research campaign for finding
and eliminating candidate mechanisms that could support bounded
functional-subject proxies: self-modeling, affect/value regulation, active
exploration, long-term learning, and self/environment boundary tracking.

Program goal status: `active_not_complete`.

Program terminal condition: `not_met`.

Program terminal verdict: `not_recorded`.

Forbidden claims remain forbidden: consciousness, subjective experience, real
emotion, autonomy, electronic life, AGI, EGO readiness, companion readiness,
stable user benefit, mainline effect, route exhaustion, and candidate validation
unless a later bounded task records computed evidence for a narrower proxy.

## Current Campaign State

Current iteration: `RESEARCH-CAMPAIGN-PHASE2C-EXECUTABLE-HARNESS-TASK-CARD-001A`

Status: `phase2c_executable_harness_task_card_validated_pending_reviewer_audit`

Current stage status: `phase2c_executable_harness_task_card_validated_pending_reviewer_audit`

Reviewer verdict: `validated_pending_reviewer_audit`

Current stage goal: Open a bounded Phase2C executable harness task card for the audited hidden-latent heldout surface contract without implementing or executing the harness.

Stage success criteria:

- executable harness task card exists
- collision record compares minimal, shortcut-baseline, and mechanism-faithful harness routes
- prior Phase 2 and Phase2B no-headroom evidence is cited
- primary-source benchmark mappings are recorded as design analogies
- focused validation passes
- candidate mechanisms remain unrun
- Phase 3 remains unopened
- route tournament remains unauthorized
- harness implementation and execution remain unauthorized

Next decision gate: Read-only reviewer audit of the validated Phase2C executable harness task-card checkpoint before implementation.

Next frontier: Run read-only reviewer audit of the validated Phase2C executable harness task-card checkpoint. Do not implement or execute the harness until that later audit succeeds; candidate mechanisms, Phase 3, route tournament, runtime/EGO mainline, push, tag, remote anchor, terminal verdicts, and route-exhaustion claims remain blocked.

## Active Checkpoint

Task card:
`docs/research_campaign/phase2c_executable_harness_task_card_001a.md`

Surface contract:
`docs/research/phase2c_hidden_latent_heldout_surface_contract_001a.md`

Checkpoint artifact:
`artifacts/research_campaign/phase2c_hidden_latent_heldout_surface_contract_001a.json`

Validation artifact:
`artifacts/research_campaign/phase2c_executable_harness_task_card_validation_001a.json`

Audit artifact:
not yet created; read-only reviewer audit is the next gate after focused validation.

Layer: engineering implementation + mechanism-hypothesis governance.

Mainline integration status: none.

Enabled status: local executable-harness task-card opening only. No harness
implementation or execution is enabled.

Real trigger evidence: audited Phase 2 and Phase2B no-headroom artifacts,
audited Phase2C hidden-latent surface contract, current repo readback, and
primary-source benchmark mappings used only as design analogies.

Claim ceiling: executable-harness task-card opening only; no mechanism
validity, learning/adaptation success, consciousness, real emotion, autonomy,
EGO readiness, companion readiness, runtime/mainline effect, route exhaustion,
terminal verdict, harness evidence, or candidate validation.

Auto-Remote-Anchor: forbidden.

## Repository Hygiene Checkpoint

Maintenance task:
`docs/research_campaign/worktree_batch_cleanup_task_card_001a.md`

Status: `worktree_batch_cleanup_completed_local_batch_commits_clean_record_corrected_pending_closeout_commit`

User-authorized local action: classify dirty/untracked paths, keep existing
ignore rules for temporary cache/log noise, and create exact-path local commit
batches for durable governance, source/test, and artifact files.

Forbidden actions: `git add -A`, ignoring evidence-like artifacts, deleting
unowned work, push, tag, remote anchor, mechanism-candidate execution, Phase 3,
runtime/EGO mainline, and program terminal verdicts.

Task-end rule: every future task must finish with dirty-path classification and
either exact-path local commit, scoped ignore for classified temporary noise, or
an explicit dirty carry-forward blocker recorded in campaign state.
## Evidence Pointers

Standing governance card:
`docs/research_campaign/goal_stage_audit_loop_001a.md`

Standing governance appendix:
`docs/research_campaign/goal_stage_audit_loop_001a_historical_appendix.md`

Campaign progress checkpoint:
`docs/OVERALL_PROGRESS.md`

Machine scorecard:
`artifacts/research_campaign/stage_scorecard.json`

Experiment ledger:
`artifacts/research_campaign/experiment_log.jsonl`

Repeated no-headroom inputs:

- `artifacts/research_campaign/phase2_no_headroom_negative_evidence_001a.json`
- `artifacts/research_campaign/phase2b_no_headroom_negative_evidence_001a.json`
- `artifacts/research_campaign/phase2b_no_headroom_route_decision_001a.json`
- `artifacts/research_campaign/phase2b_no_headroom_route_decision_audit_001a.json`

Plan representation maintenance:

- task card: `docs/research_campaign/plan_representation_compaction_task_card_001a.md`
- validation: `artifacts/research_campaign/plan_representation_compaction_validation_001a.json`

## Campaign Loop Rules

Every future task must update campaign state immediately:

1. Before work: write or repair a bounded task card with claim ceiling,
   expected files, forbidden changes, and stop condition.
2. During work: preserve failures and blockers in the ledger; do not wait for a
   pass.
3. After work: append `experiment_log.jsonl`, update `stage_scorecard.json`,
   update `docs/OVERALL_PROGRESS.md`, and record the next minimal closed-loop
   action.
4. If two consecutive tasks do not increase discriminative evidence, route to
   `needs_reframing`; do not continue patching toward a pass.
5. On every resume, read `docs/OVERALL_PROGRESS.md`,
   `artifacts/research_campaign/stage_scorecard.json`, and
   `artifacts/research_campaign/experiment_log.jsonl` before continuing.

## Research Phases

Phase 1: Problem formalization into measurable proxy variables.

Phase 2: Baseline-first headroom; stop on fair baseline saturation.

Phase 3: Mechanism search only inside measured-headroom environments.

Phase 4: Structure extraction from pass and fail evidence using low-complexity,
replayable structures.

Phase 5: Large-scale validation with distribution shift, counterfactuals,
interventions, ablations, source deletion, replay recomputation, and leakage
positive controls.

Phase 6: Local formalization only for stable, reproducible, baseline-resistant
structures. This cannot prove consciousness.

Phase 1 through Phase 6 may repeat. A single task card, phase pass, local
validation pass, or chat-only reviewer verdict cannot complete the program.

## Standing Anti-False-Pass Rules

- No static verdict dictionaries, handwritten scores, unconditional clean
  reports, or tests that only assert pass.
- Baselines must be independent callable implementations under the same budget
  and input boundary as the candidate.
- Ablations must rerun episodes under real interventions.
- Leakage scans must include a real scanner and at least one positive control.
- Replay must recompute behavior from serialized state and observation.
- Any unused frozen seed, heldout context, train context, or counterfactual pair
  blocks the evidence claim.

## Next Minimal Closed-Loop Action

Run read-only reviewer audit for
`RESEARCH-CAMPAIGN-PHASE2C-EXECUTABLE-HARNESS-TASK-CARD-001A` before any
harness implementation or execution.

Candidate mechanisms, Phase 3, route tournament, harness implementation,
harness execution, runtime/EGO mainline, push, tag, remote anchor, terminal
verdicts, and route-exhaustion claims remain blocked.
