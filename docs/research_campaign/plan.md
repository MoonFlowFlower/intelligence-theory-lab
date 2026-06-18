# Strict Intelligence Mechanism Research Campaign Plan

Last updated: 2026-06-18T12:55:14-05:00

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

Current iteration: `RESEARCH-CAMPAIGN-PHASE2C-CANDIDATE-FREE-BASELINE-STRESS-EXECUTION-001A`

Status: `phase2c_candidate_free_baseline_stress_audited_success_post_result_route_check_next`

Current stage status: `phase2c_candidate_free_baseline_stress_audited_success_post_result_route_check_next`

Reviewer verdict: `success_reached`

Current stage goal: Execute and audit candidate-free Phase2C baseline stress before any candidate mechanism work.

Stage success criteria:

- execution task card exists
- execution task card validation passes
- candidate-free baseline-stress wrapper and focused tests exist under isolated paths
- focused wrapper tests and parent Phase2C hidden-latent harness tests pass
- CLI run generates all required baseline-stress artifacts
- read-only audit returns `success_reached`
- stress run uses at least 5 seeds, 3 train families, 3 heldout families, and 4 episodes per family
- trace row count is `120`
- required baseline set is complete
- lookup-family baseline tie is preserved as the reason immediate candidate work remains premature
- parent Phase2C hidden-latent harness source/tests/repaired outputs are unchanged
- candidate mechanisms remain unrun
- Phase 3 remains unopened
- route tournament remains unauthorized
- runtime/EGO mainline, push, tag, remote anchor, terminal verdict, and
  route-exhaustion claims remain blocked

Next decision gate: Post-result route check over the audited candidate-free Phase2C baseline-stress result.

Next frontier: Open a bounded post-result route check for `artifacts/research_campaign/phase2c_candidate_free_baseline_stress_001a.json` and `artifacts/research_campaign/phase2c_candidate_free_baseline_stress_audit_001a.json` before any candidate mechanism work. Candidate mechanisms, Phase 3, route tournament, runtime/EGO mainline, push, tag, remote anchor, terminal verdicts, and route-exhaustion claims remain blocked.

## Active Checkpoint

Task card:
`docs/research_campaign/phase2c_candidate_free_baseline_stress_execution_task_card_001a.md`

Validation artifact:
`artifacts/research_campaign/phase2c_candidate_free_baseline_stress_execution_task_card_validation_001a.json`

Audit artifact:
`artifacts/research_campaign/phase2c_candidate_free_baseline_stress_audit_001a.json`

Execution summary:
`artifacts/research_campaign/phase2c_candidate_free_baseline_stress_001a.json`

Raw output directory:
`artifacts/phase2c_candidate_free_baseline_stress_001a/`

Result artifact:
`artifacts/phase2c_candidate_free_baseline_stress_001a/result.json`

Parent baseline-stress task card:
`docs/research_campaign/phase2c_candidate_free_baseline_stress_task_card_001a.md`

Parent baseline-stress task-card validation:
`artifacts/research_campaign/phase2c_candidate_free_baseline_stress_task_card_validation_001a.json`

Parent baseline-stress task-card audit:
`artifacts/research_campaign/phase2c_candidate_free_baseline_stress_task_card_audit_001a.json`

Source route-check task card:
`docs/research_campaign/phase2c_hidden_latent_post_result_route_check_task_card_001a.md`

Source route-check artifact:
`artifacts/research_campaign/phase2c_hidden_latent_post_result_route_check_001a.json`

Source route-check audit:
`artifacts/research_campaign/phase2c_hidden_latent_post_result_route_check_audit_001a.json`

Selected route:
`candidate_free_baseline_stress_task_card`

Preserved command failure artifact:
`artifacts/research_campaign/phase2c_hidden_latent_harness_execution_command_failure_001a.json`

Command repair validation artifact:
`artifacts/research_campaign/phase2c_hidden_latent_harness_execution_command_repair_validation_001a.json`

Execution summary artifact:
`artifacts/research_campaign/phase2c_hidden_latent_harness_execution_001a.json`

Repair task card:
`docs/research_campaign/phase2c_hidden_latent_harness_execution_output_repair_task_card_001a.md`

Repair task-card validation:
`artifacts/research_campaign/phase2c_hidden_latent_harness_execution_output_repair_task_card_validation_001a.json`

Repair execution artifact:
`artifacts/research_campaign/phase2c_hidden_latent_harness_execution_output_repair_001a.json`

Repaired output directory:
`artifacts/phase2c_hidden_latent_harness_001a_repaired_001a/`

Repair audit artifact:
`artifacts/research_campaign/phase2c_hidden_latent_harness_execution_output_repair_audit_001a.json`

Audit artifact:
`artifacts/research_campaign/phase2c_hidden_latent_harness_execution_task_card_audit_001a.json`

Layer: engineering implementation + mechanism-hypothesis governance.

Mainline integration status: none.

Enabled status: local Phase2C candidate-free baseline-stress wrapper executed and audited success.

Real trigger evidence: CLI run of
`phase2c_candidate_free_baseline_stress_001a.runner` generated result,
baseline, leakage, replay, ablation, provenance, failure-manifest, and trace
artifacts. The run used 5 seeds, 3 train families, 3 heldout families, 4
episodes per family, and 120 trace rows. The strongest fair baseline was
`episodic_traversal` with macro accuracy `0.2833333333333333`; `graph_cache`
also tied strongest, preserving the cheap lookup-family explanation.

Claim ceiling: candidate-free Phase2C baseline-stress execution evidence only;
no candidate validation, no mechanism validity, no learning/adaptation success,
no consciousness, no real emotion, no autonomy, no EGO readiness, no companion
readiness, no runtime/mainline effect, no route exhaustion, no terminal verdict,
and no program completion.

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

Open a bounded post-result route check over the audited candidate-free Phase2C
baseline-stress result before any candidate mechanism work.

Candidate mechanisms, Phase 3, route tournament, runtime/EGO mainline, push,
tag, remote anchor, terminal verdicts, and route-exhaustion claims remain
blocked.
