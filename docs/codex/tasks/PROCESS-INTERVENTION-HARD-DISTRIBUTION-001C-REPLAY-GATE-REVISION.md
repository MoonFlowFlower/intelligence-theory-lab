# PROCESS-INTERVENTION-HARD-DISTRIBUTION-001C-REPLAY-GATE-REVISION Task Card

Task ID: PROCESS-INTERVENTION-HARD-DISTRIBUTION-001C-REPLAY-GATE-REVISION

Layer: bounded replay-gate taxonomy revision only.

## Problem Definition

`PROCESS-INTERVENTION-HARD-DISTRIBUTION-001B-EXECUTABLE-PREFLIGHT` failed
under its historical gate because `trace_only_replay` matched the witness trace
at `1.0`. `PROCESS-INTERVENTION-HARD-DISTRIBUTION-001B-TRACE-REPLAY-RCA-001A`
adjudicated `trace_only_replay` as `trace_integrity_hygiene` because it used
committed target trace records, including target outcomes, future behaviors,
and process signatures.

No target-free generative replay challenger existed in 001B. This task revises
future process-intervention replay-gate taxonomy without rewriting 001B,
removing `trace_only_replay` from the historical failure reasoning, or claiming
001B pass.

## Current Stage

Evidence-gate revision only. No mechanism implementation. No mechanism
training. No Gate1 authorization. No bridge authorization. No EGO mainline
authorization. No model-class reset authorization. No mechanism tournament
authorization. No historical verdict rewrite.

## Anti-Sycophancy Audit

Strongest baseline explanation: the historical 001B gate failed because its
predeclared failure condition treated any fair-control match as blocking, and
`trace_only_replay` deterministically replayed committed target trace records.

Strongest reason this task may be invalid: if this revision is applied
retroactively, it becomes a post-hoc rescue of a failed historical gate rather
than a future-facing taxonomy correction.

Falsifier for the current framing: if `trace_only_replay` did not read committed
target trace records and instead emitted heldout outcomes, future behaviors, and
process signatures before target-trace access, then it should remain an
independent generative replay challenger.

Evidence still insufficient: a clean taxonomy does not prove any mechanism,
does not prove future Gate1 readiness, and does not prove the future challenger
suite is exhaustive or statistically powered.

This task tests replay-gate wording and access taxonomy only. It does not test
mechanism validity and does not produce behavioral resemblance evidence.

## Hypothesis

Future process-intervention gates can avoid false blocking by separating:

```text
trace_integrity_hygiene
behavioral_replay_baseline
target_free_generative_replay_challenger
```

Only target-free generative replay challengers should count as independent
mechanism-challenger baselines. Trace-only replay remains mandatory for replay
integrity, but its success is hygiene evidence rather than mechanism
equivalence evidence.

## Baseline

Historical 001B treated `trace_only_replay` as a blocking fair control and
therefore failed when `trace_only_replay` matched at `1.0`.

## Frozen Inputs

Read only:

```text
artifacts/process_intervention_hard_distribution_001b/result.json
artifacts/process_intervention_hard_distribution_001b/control_comparison.json
artifacts/process_intervention_hard_distribution_001b/baseline_comparison.json
artifacts/process_intervention_hard_distribution_001b/ablation_report.json
artifacts/process_intervention_hard_distribution_001b/replay_report.json
artifacts/process_intervention_hard_distribution_001b/heldout_report.json
artifacts/process_intervention_hard_distribution_001b/failure_manifest.json
artifacts/process_intervention_hard_distribution_001b/trace.jsonl
artifacts/process_intervention_hard_distribution_001b/frozen_inputs.json
artifacts/process_intervention_hard_distribution_001b/claim_ceiling.txt
artifacts/process_intervention_hard_distribution_001b_trace_replay_rca_001a/replay_control_adjudication.json
artifacts/process_intervention_hard_distribution_001b_trace_replay_rca_001a/claim_ceiling.txt
artifacts/process_intervention_hard_distribution_001a/hard_distribution_spec.json
artifacts/process_intervention_hard_distribution_001a/frozen_inputs.json
artifacts/process_intervention_hard_distribution_001a/distribution_shortcut_audit.json
artifacts/process_intervention_hard_distribution_001a/fair_control_budget_spec.json
artifacts/process_intervention_hard_distribution_001a/heldout_composition_manifest.json
artifacts/process_intervention_hard_distribution_001a/ablation_hook_manifest.json
docs/process_intervention_preflight_001a/trace_replay_contract.md
docs/process_intervention_preflight_001a/real_control_implementation_contract.md
docs/GATE1-REPLAY-CONSOLIDATION-TASKCARD-001A.md
docs/GATE1-REPLAY-CONSOLIDATION-TASKCARD-001B.md
docs/GATE1-REPLAY-CONSOLIDATION-EXEC-TASKCARD-001.md
```

## Required Actions

1. Produce future-facing replay taxonomy artifacts.
2. Classify `trace_only_replay` as `trace_integrity_hygiene`, not an independent
mechanism challenger.
3. Define target-free access rules for a future generative replay challenger.
4. Define future pass/fail semantics without changing historical 001B verdicts.
5. Preserve non-replay fair controls and future ablation requirements.
6. Keep all authorization flags false.

## Required Artifacts

```text
artifacts/process_intervention_hard_distribution_001c_replay_gate_revision/replay_gate_revision_result.json
artifacts/process_intervention_hard_distribution_001c_replay_gate_revision/replay_control_taxonomy.json
artifacts/process_intervention_hard_distribution_001c_replay_gate_revision/future_gate_semantics.json
artifacts/process_intervention_hard_distribution_001c_replay_gate_revision/historical_verdict_preservation_note.txt
artifacts/process_intervention_hard_distribution_001c_replay_gate_revision/claim_ceiling.txt
```

## Baseline Requirement

Future gates must preserve:

```text
online_count_statistic
count_table
graph_cache
transition_table
successor_map
summary_retrieval or equivalent
behavior_only_replay
target_free_generative_replay_challenger if replay baseline is claimed
```

## Ablation Requirement

Future process-intervention evidence must still require:

```text
learning_freeze
history_replacement
counterfactual_action_contrast
outcome_perturbation if predeclared
heldout_composition_evaluation
```

## Trace / Replay Requirement

This task does not execute a new mechanism replay. It revises future replay-gate
taxonomy only.

Trace-only replay remains mandatory as hygiene, but is not sufficient mechanism
evidence and must not block mechanism evidence when its only access is committed
target trace replay.

## Acceptance Gate

Pass only if:

```text
replay control taxonomy is explicit
trace-only replay is classified as hygiene, not independent mechanism challenger
future generative replay challenger requirements are target-free
historical 001B verdict remains unchanged
no old artifacts are modified
future gate semantics are machine-readable
all authorization flags are false
claim ceiling remains bounded replay-gate taxonomy revision only
```

## Negative Checks

Fail if the task changes the historical 001B verdict, edits old 001B artifacts,
removes `trace_only_replay` from historical failure reasoning, reclassifies 001B
as pass, treats trace hygiene as mechanism evidence, omits a target-free
generative replay challenger from future gate design, authorizes Gate1 / bridge
/ EGO / model-class reset / mechanism tournament, weakens fair controls, weakens
replay integrity requirements, changes thresholds post hoc, or implements a new
mechanism.

## Claim Ceiling

Maximum claim:

```text
bounded replay-gate taxonomy revision only
```

This cannot prove mechanism validity, 001B pass, theory validity, theory
falsity, Gate1 readiness, bridge readiness, EGO readiness, agency,
consciousness, companion readiness, or model-class reset necessity.

## Rollback Plan

All changes must be isolated to:

```text
artifacts/process_intervention_hard_distribution_001c_replay_gate_revision/
docs/codex/tasks/PROCESS-INTERVENTION-HARD-DISTRIBUTION-001C-REPLAY-GATE-REVISION.md
tests/test_process_intervention_hard_distribution_001c_replay_gate_revision.py
```

If overreach is detected, revert only the 001C commit.
