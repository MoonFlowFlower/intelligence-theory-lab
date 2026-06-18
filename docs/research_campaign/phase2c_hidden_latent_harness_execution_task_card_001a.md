# Phase2C Hidden-Latent Harness Execution Task Card 001A

Task ID:
`RESEARCH-CAMPAIGN-PHASE2C-HIDDEN-LATENT-HARNESS-EXECUTION-TASK-CARD-001A`

Status: pending focused validation.

This card opens a bounded future execution checkpoint for the reviewed
Phase2C hidden-latent harness implementation. It does not run the harness and
does not generate output artifacts.

## Problem Definition

The Phase2C hidden-latent harness source/tests are implemented and
reviewer-audited, but no evidence run exists. A separate execution card is
required before running the local runner so that artifact paths, stop
conditions, claim ceiling, and post-run audit requirements are fixed before any
score-bearing output is generated.

## Current Layer

Engineering implementation + mechanism-hypothesis governance.

Mainline integration status: none.

Enabled status: execution task-card opening only. Harness execution remains
disabled until this card is focused-validated and read-only reviewer-audited.

Real trigger evidence:

- reviewed implementation audit:
  `artifacts/research_campaign/phase2c_hidden_latent_harness_implementation_audit_001a.json`;
- implementation validation:
  `artifacts/research_campaign/phase2c_hidden_latent_harness_implementation_validation_001a.json`;
- source package:
  `src/phase2c_hidden_latent_harness_001a/`;
- tests:
  `tests/phase2c_hidden_latent_harness_001a/`.

Claim ceiling: execution task-card opening only. No harness execution evidence,
baseline result, ablation result, replay evidence, candidate validation,
mechanism validity, learning/adaptation success, subjectivity, consciousness,
real emotion, autonomy, EGO readiness, companion readiness, runtime/mainline
effect, route exhaustion, terminal verdict, or program completion claim.

Auto-Remote-Anchor: forbidden.

## Bounded Audit Before Future Execution

Real objective: allow one later bounded local execution of the reviewed
candidate-free harness while preventing a score-bearing run from being
mistaken for a mechanism pass, candidate validation, Phase 3 opening, or
program terminal verdict.

Strongest baseline explanation: even after execution, the strongest fair
baseline may saturate the oracle again, or the implemented surface may fail
leakage, replay, ablation, or provenance gates.

Strongest reason this task may be invalid: if this card permits execution
without a post-run reviewer audit or without exact artifact paths, any generated
score could become an unaudited false-positive boundary.

Falsifier for this card: missing runner command, missing output artifact list,
missing post-run reviewer audit requirement, missing no-candidate/no-Phase3
block, missing no-remote-anchor block, or any current harness output artifact.

Evidence that would still be insufficient: a successful command exit without
machine-readable artifacts, provenance, replay, leakage-positive controls,
baseline battery, ablation checks, and campaign ledger updates.

## Collision Record

### Candidate A: Run the harness immediately

Evidence it would produce: local output artifacts and a runner exit code.

Strongest cheap baseline that could match it: an unaudited run can look like
progress even if a baseline saturates the oracle or a control path fails.

Leakage / hard-coding risk: high, because output would exist before the
execution scope and post-run audit gates are frozen.

Smallest falsifying test: any file appears under
`artifacts/phase2c_hidden_latent_harness_001a/` before this card is validated
and reviewer-audited.

Expected failure mode: score-bearing artifacts are generated before the
campaign state has a bounded review path.

Decision: rejected for this checkpoint.

### Candidate B: Execution task card only

Evidence it would produce: frozen execution command, output paths, stop
conditions, and post-run audit requirement.

Strongest cheap baseline that could match it: task-card creation alone does
not prove the harness will execute or produce valid evidence.

Leakage / hard-coding risk: low for this checkpoint if no execution occurs.

Smallest falsifying test: output directory exists or runner command is executed
during this task-card-opening checkpoint.

Expected failure mode: later execution fails or returns no-headroom/invalid
evidence; that remains valid evidence and must not be patched into a pass.

Decision: selected for this checkpoint.

Selected route: `execution_task_card_only_pending_reviewer_audit`.

## Mainline Target

No EGO runtime or mainline target exists. The future execution remains a local
offline harness run only.

## Enabled-State Requirement

This checkpoint enables only validation and reviewer audit of this execution
card.

Future harness execution remains disabled until:

- this card exists;
- focused validation passes;
- read-only reviewer audit returns `success_reached`;
- campaign state records the audit result;
- no stop condition remains active;
- worktree status and exact output paths are cleanly classified.

## Future Runner Command

Future execution, if later authorized by this card's reviewer audit, must use:

```text
python -m phase2c_hidden_latent_harness_001a.runner --output-dir artifacts/phase2c_hidden_latent_harness_001a
```

## Future Required Output Artifacts

The future run must write under:

```text
artifacts/phase2c_hidden_latent_harness_001a/
```

Required files:

- `result.json`;
- `trace.jsonl`;
- `baseline_comparison.json`;
- `ablation_report.json`;
- `replay_report.json`;
- `leakage_report.json`;
- `failure_manifest.json`.

The future campaign summary artifact, if generated, must be:

```text
artifacts/research_campaign/phase2c_hidden_latent_harness_execution_001a.json
```

## Hypothesis

A reviewed local execution task card can constrain the next run so generated
artifacts become auditable local evidence rather than an uncontrolled pass
claim.

This checkpoint does not test harness behavior.

## Strongest Baseline

The future execution must retain the full implemented baseline registry:

- random;
- majority;
- observation_only;
- lookup;
- count_table;
- transition_table;
- graph_cache;
- successor_map;
- nearest_neighbor;
- fsm_planner;
- episodic_traversal;
- trace_only_replay;
- exhaustive_legal_query.

## Ablation Requirement

The future execution must retain the implemented ablation controls:

- memory_deletion;
- latent_rule_swap;
- heldout_task_family_transfer;
- partial_observation_ablation;
- exploration_budget_ablation;
- cross_episode_reset;
- source_memory_deletion;
- spurious_token_injection_removal;
- observation_field_masking.

## Trace / Replay Requirement

The future replay report must recompute from:

- serialized_state;
- current_observation;
- legal_action_or_query_schema;
- budget_state;
- latent_belief_or_memory_state.

Hash-only comparison or stored-output-only replay cannot satisfy this card.

## Computed-Evidence Provenance Gate

Future execution evidence must record callable producer provenance for:

- surface_generation;
- baseline_battery;
- leakage_scan;
- replay_recomputation;
- ablation_plan.

Every provenance record must include producer_function, input_artifacts,
run_id, seed_context_episode_ids, aggregation_rule, code_path_hash, and
consumed_by_final_verdict.

## Acceptance Gate

This task-card-opening checkpoint is acceptable only if:

- this card exists;
- required command and artifact paths are present;
- focused validation passes;
- no files exist under `artifacts/phase2c_hidden_latent_harness_001a/`;
- no future execution summary exists at
  `artifacts/research_campaign/phase2c_hidden_latent_harness_execution_001a.json`;
- candidate mechanisms remain unrun;
- Phase 3 remains unopened;
- route tournament remains unauthorized;
- harness execution remains unauthorized until reviewer audit succeeds;
- push, tag, and remote anchor remain forbidden.

## Stop Conditions

Stop and record a blocker if:

- the runner command is executed in this checkpoint;
- any harness output artifact is generated in this checkpoint;
- a candidate mechanism is implemented or scored;
- Phase 3 is opened;
- route tournament is authorized;
- runtime/EGO mainline is touched;
- validation or JSON/JSONL parse fails;
- campaign state disagrees about the current frontier;
- push, tag, or remote anchor is attempted.

## Rollback Plan

If validation fails, preserve the failed validation artifact and repair only
this execution card and campaign bookkeeping. Do not delete or rewrite the
reviewed source/test implementation or previous audits.

If a harness output artifact appears during this checkpoint, stop, classify it
as unauthorized execution output, and do not use it as evidence.

## Expected Changed Files

This execution-card-opening checkpoint may change only:

- `docs/research_campaign/phase2c_hidden_latent_harness_execution_task_card_001a.md`;
- `artifacts/research_campaign/phase2c_hidden_latent_harness_execution_task_card_validation_001a.json`;
- `docs/research_campaign/plan.md`;
- `docs/OVERALL_PROGRESS.md`;
- `artifacts/research_campaign/stage_scorecard.json`;
- `artifacts/research_campaign/experiment_log.jsonl`.

## Forbidden Changes

- Do not execute the harness.
- Do not generate files under `artifacts/phase2c_hidden_latent_harness_001a/`.
- Do not generate
  `artifacts/research_campaign/phase2c_hidden_latent_harness_execution_001a.json`.
- No source implementation changes.
- No test changes.
- No candidate mechanism implementation.
- No candidate scoring.
- No Phase 3 mechanism search.
- No route tournament.
- No runtime/EGO mainline changes.
- No UI, LLM, AIRI, deployment, companion, relationship-learning, emotion, or
  proactive-behavior changes.
- No push, tag, or remote anchor.

## Local Commit

Local commit is authorized only for this durable execution-card-opening
checkpoint after focused validation passes, exact-path staging is verified,
and the staged set is limited to the expected changed files.

## Immediate Next Action

Run focused validation of this execution task card. If validation passes, run a
read-only reviewer audit before any harness execution or output artifact
generation.
