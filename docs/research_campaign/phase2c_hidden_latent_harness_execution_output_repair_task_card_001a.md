# Phase2C Hidden-Latent Harness Execution Output Repair Task Card 001A

Task ID:
`RESEARCH-CAMPAIGN-PHASE2C-HIDDEN-LATENT-HARNESS-EXECUTION-OUTPUT-REPAIR-001A`

Status: opened pending focused validation.

## Problem Definition

The repaired Phase2C command executed and wrote the required filenames under
`artifacts/phase2c_hidden_latent_harness_001a/`, but the output is invalid as
execution evidence. `result.json` reports `implemented_not_executed`,
`harness_execution_claim=false`, and `trace.jsonl` is empty.

The invalid output is preserved in:

```text
artifacts/research_campaign/phase2c_hidden_latent_harness_execution_001a.json
artifacts/phase2c_hidden_latent_harness_001a/
```

## Current Layer

Engineering implementation + mechanism-hypothesis testing.

Mainline integration status: none.

Enabled status: local source/test repair only. No EGO runtime, UI, LLM,
AIRI, deployment, companion behavior, candidate mechanism, Phase 3, or route
tournament is authorized.

Real trigger evidence: repaired command exit 0, required filenames generated,
`result.json` disclaims execution, and `trace.jsonl` has zero rows.

Claim ceiling: source repair and repaired local harness-output validation only;
no candidate validation, mechanism validity, learning/adaptation success,
subjectivity, consciousness, real emotion, autonomy, EGO readiness, companion
readiness, runtime/mainline effect, route exhaustion, terminal verdict, or
program completion claim.

Auto-Remote-Anchor: forbidden.

## Bounded Audit

Real objective: repair the local Phase2C harness output path so a future run
can produce a non-empty trace, an execution-scoped result verdict, and persisted
computed provenance without claiming a candidate mechanism pass.

Strongest baseline explanation: even with a repaired output path, baseline
results may remain weak or a later reviewer may find the trace/provenance
insufficient.

Strongest reason this repair may be invalid: changing result wording alone
could turn a report into a pass-shaped artifact while trace or provenance
remains insufficient.

Falsifier: a repaired run still has empty trace rows, `harness_execution_claim`
false, missing computed provenance, or an execution verdict that exceeds the
candidate-free claim ceiling.

Evidence still insufficient: a successful command exit without non-empty trace
rows, replay input readback, leakage controls, baseline battery, ablation
controls, and persisted provenance.

## Collision Record

### Candidate A: Reword `result.json` only

Evidence it would produce: a pass-shaped result file.

Strongest cheap baseline that could match it: static report mutation.

Leakage / hard-coding risk: high.

Smallest falsifying test: `trace.jsonl` remains empty or provenance is missing.

Expected failure mode: claim inflation without evidence-path repair.

Decision: rejected.

### Candidate B: Preserve invalid output and repair trace/result/provenance path

Evidence it would produce: tests that fail on the current empty-trace output,
then a repaired run in a new output directory with non-empty trace rows,
execution-scoped result fields, and persisted computed provenance.

Strongest cheap baseline that could match it: file generation with static
trace rows. The repair must build trace rows from generated episodes and
callable replay inputs.

Leakage / hard-coding risk: medium; candidate-visible rows must stay free of
hidden rule IDs, task family IDs, target-action labels, and answer maps.

Smallest falsifying test: trace rows are empty, candidate-visible rows leak
hidden fields, or provenance is absent/not consumed.

Expected failure mode: repaired output still cannot satisfy execution evidence.

Decision: selected.

### Candidate C: Rerun the current harness without source repair

Evidence it would produce: the same invalid output shape.

Strongest cheap baseline that could match it: current runner already generates
files while disclaiming execution.

Leakage / hard-coding risk: low, but it cannot answer the task.

Smallest falsifying test: repeated `implemented_not_executed` result.

Expected failure mode: no progress beyond repeated invalid output.

Decision: rejected.

## Mainline Target

No EGO mainline target exists. This is an offline local harness repair only.

## Hypothesis

If `run_harness` constructs trace rows from generated episodes and callable
replay inputs, records execution-scoped result fields, and persists computed
provenance, then a repaired output run can become auditable local harness
execution evidence while staying below candidate-validation and mechanism
claims.

## Strongest Baseline

The repaired run must preserve the existing callable baseline battery:
random, majority, observation_only, lookup, count_table, transition_table,
graph_cache, successor_map, nearest_neighbor, fsm_planner,
episodic_traversal, trace_only_replay, and exhaustive_legal_query.

## Ablation Requirement

The repaired run must preserve all existing ablation controls and keep them
consumed by the final verdict.

## Trace / Replay Requirement

Trace rows must be non-empty and each row must include replay inputs derived
from the generated episode:

- serialized_state;
- current_observation;
- legal_action_or_query_schema;
- budget_state;
- latent_belief_or_memory_state.

Candidate-visible payloads in trace rows must not expose hidden rule IDs, task
family IDs, answer maps, target-action labels, or serialized state.

## Computed-Evidence Provenance Gate

The repaired run must persist computed provenance as
`computed_evidence_provenance.json` in the repaired output directory. Each
record must include producer_function, input_artifacts, run_id,
seed_context_episode_ids, aggregation_rule, code_path_hash, and
consumed_by_final_verdict.

## Acceptance Gate

- Add a failing test that catches the current empty-trace / no-execution-claim
  output.
- Repair only `src/phase2c_hidden_latent_harness_001a/runner.py` and focused
  tests.
- Targeted tests pass.
- Repaired run writes to
  `artifacts/phase2c_hidden_latent_harness_001a_repaired_001a/`.
- Invalid original output remains preserved and is not deleted.
- Repaired output has non-empty trace rows.
- Repaired result stays candidate-free and below mechanism-validity claims.
- JSON/JSONL parse checks pass.

## Stop Conditions

Stop and preserve a failure if:

- the invalid original output is deleted;
- repaired trace rows are empty;
- candidate-visible trace payloads leak hidden labels or answer fields;
- provenance is missing or static;
- candidate mechanisms are implemented or scored;
- Phase 3 or route tournament is opened;
- runtime/EGO mainline is touched;
- push, tag, or remote anchor is attempted.

## Rollback Plan

If repair fails, preserve the failing test/output and revert only the repair
attempt through a later explicit cleanup task. Do not delete the already
preserved invalid execution output.

## Expected Changed Files

- `docs/research_campaign/phase2c_hidden_latent_harness_execution_output_repair_task_card_001a.md`;
- `artifacts/research_campaign/phase2c_hidden_latent_harness_execution_output_repair_task_card_validation_001a.json`;
- `src/phase2c_hidden_latent_harness_001a/runner.py`;
- `tests/phase2c_hidden_latent_harness_001a/test_phase2c_hidden_latent_harness_001a.py`;
- `artifacts/phase2c_hidden_latent_harness_001a_repaired_001a/`;
- `artifacts/research_campaign/phase2c_hidden_latent_harness_execution_output_repair_001a.json`;
- `docs/research_campaign/plan.md`;
- `docs/OVERALL_PROGRESS.md`;
- `artifacts/research_campaign/stage_scorecard.json`;
- `artifacts/research_campaign/experiment_log.jsonl`.

## Forbidden Changes

- Do not delete or overwrite `artifacts/phase2c_hidden_latent_harness_001a/`.
- Do not implement or score a candidate mechanism.
- Do not open Phase 3 or a route tournament.
- Do not touch EGO runtime, UI, LLM integration, AIRI integration,
  deployment, companion behavior, relationship learning, emotion systems, or
  proactive behavior.
- Do not push, tag, or remote-anchor.

## Immediate Next Action

Run focused validation of this repair task card. If validation passes, add the
failing test first, then repair the runner.
