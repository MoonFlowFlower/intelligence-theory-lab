# Strict Intelligence Mechanism Research Campaign Plan

Last updated: 2026-06-18T09:04:42-05:00

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

Current iteration: `RESEARCH-CAMPAIGN-PHASE2C-HIDDEN-LATENT-HARNESS-IMPLEMENTATION-001A`

Status: `phase2c_hidden_latent_harness_implementation_reviewed_success`

Current stage status: `phase2c_hidden_latent_harness_implementation_reviewed_success`

Reviewer verdict: `success_reached`

Current stage goal: Complete read-only reviewer audit of the frozen-path Phase2C hidden-latent harness source/tests before harness execution.

Stage success criteria:

- source package exists under `src/phase2c_hidden_latent_harness_001a/`
- tests exist under `tests/phase2c_hidden_latent_harness_001a/`
- TDD RED missing-package failure is recorded
- targeted unit tests pass
- baseline registry is callable and complete
- leakage positive controls are callable
- replay recomputes from required inputs
- ablation controls are callable
- provenance verifier rejects missing producer records
- initial validation path-predicate failure is preserved and repaired
- read-only reviewer audit returns `success_reached`
- harness output directory remains absent
- candidate mechanisms remain unrun
- Phase 3 remains unopened
- route tournament remains unauthorized
- harness execution remains unauthorized

Next decision gate: Separate bounded Phase2C harness execution task card required before running the harness or generating output artifacts.

Next frontier: Open a separate bounded Phase2C harness execution task card before running the harness or generating output artifacts. Candidate mechanisms, Phase 3, route tournament, runtime/EGO mainline, push, tag, remote anchor, terminal verdicts, and route-exhaustion claims remain blocked.

## Active Checkpoint

Task card:
`docs/research_campaign/phase2c_harness_implementation_freeze_task_card_001a.md`

Source paths:
`src/phase2c_hidden_latent_harness_001a/`

Test path:
`tests/phase2c_hidden_latent_harness_001a/`

Surface contract:
`docs/research/phase2c_hidden_latent_heldout_surface_contract_001a.md`

Checkpoint artifact:
`artifacts/research_campaign/phase2c_hidden_latent_heldout_surface_contract_001a.json`

Validation artifact:
`artifacts/research_campaign/phase2c_hidden_latent_harness_implementation_validation_001a.json`

Audit artifact:
`artifacts/research_campaign/phase2c_hidden_latent_harness_implementation_audit_001a.json`

Layer: engineering implementation + mechanism-hypothesis governance.

Mainline integration status: none.

Enabled status: local Phase2C hidden-latent harness source/tests reviewed
success pending execution task card. Harness execution remains disabled.

Real trigger evidence: read-only reviewer audit over committed frozen-path
source/tests, validation artifact, targeted unit tests, no harness output
directory, and campaign state readback.

Claim ceiling: read-only reviewer audit of frozen-path Phase2C harness
source/test implementation only; no harness execution, no output artifacts, no
baseline result, no ablation result, no replay evidence, no candidate
validation, no mechanism validity, learning/adaptation success, consciousness,
real emotion, autonomy, EGO readiness, companion readiness, runtime/mainline
effect, route exhaustion, terminal verdict, or program completion claim.

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

Open a separate bounded Phase2C harness execution task card before running the
harness or generating output artifacts.

Candidate mechanisms, Phase 3, route tournament, harness execution,
runtime/EGO mainline, push, tag, remote anchor, terminal verdicts, and
route-exhaustion claims remain blocked.
