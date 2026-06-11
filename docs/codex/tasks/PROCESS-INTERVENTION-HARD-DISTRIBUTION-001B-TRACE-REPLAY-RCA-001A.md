# PROCESS-INTERVENTION-HARD-DISTRIBUTION-001B-TRACE-REPLAY-RCA-001A Task Card

Task ID: PROCESS-INTERVENTION-HARD-DISTRIBUTION-001B-TRACE-REPLAY-RCA-001A

Layer: bounded replay-control adjudication only.

## Problem Definition

`PROCESS-INTERVENTION-HARD-DISTRIBUTION-001B-EXECUTABLE-PREFLIGHT` failed
because `trace_only_replay` matched the witness trace at `1.0`. All non-replay
fair controls no longer matched perfectly; the best non-replay control was
`count_table = 0.4167`.

The ambiguity is whether `trace_only_replay` is a valid independent fair
mechanism-challenger control, or only a trace-integrity / replay-hygiene check.

## Current Stage

No Gate1 authorization. No bridge authorization. No EGO mainline authorization.
No model-class reset authorization. No mechanism tournament authorization. No
mechanism implementation authorization. No verdict rewrite authorization.

## Hypothesis

If `trace_only_replay` directly replays committed witness trace records, then
its `1.0` match is expected and should be classified as replay/integrity
hygiene, not as independent mechanism-equivalence evidence. If it predicts
heldout behavior without target-trace access, then it remains a valid fair
challenger.

## Frozen Inputs

Use only existing 001B artifacts:

```text
result.json
control_comparison.json
baseline_comparison.json
ablation_report.json
replay_report.json
heldout_report.json
failure_manifest.json
trace.jsonl
frozen_inputs.json
claim_ceiling.txt
```

## Required Actions

1. Read the hard-distribution 001B artifacts.
2. Identify exactly what access `trace_only_replay` had.
3. Determine whether `trace_only_replay` used committed target trace records.
4. Determine whether it made any heldout/generative prediction without direct
target-trace access.
5. Compare `trace_only_replay` with `behavior_only_replay` and non-replay fair
controls.
6. Classify replay controls into:

```text
trace_integrity_hygiene
behavioral_replay_baseline
generative_replay_challenger
```

7. Produce `replay_control_adjudication.json`.
8. Produce `claim_ceiling.txt`.

## Negative Checks

Fail if the task rewrites the 001B verdict, modifies old 001B artifacts,
removes `trace_only_replay` from the historical 001B failure condition,
reinterprets 001B as pass, authorizes Gate1 / bridge / EGO / model-class reset
/ mechanism tournament, or changes any threshold.

## Acceptance Gate

Pass only if:

```text
replay_control_adjudication.json is JSON-parseable
old 001B artifacts remain unchanged
trace_only_replay access contract is explicitly classified
distinction between trace hygiene and generative replay baseline is stated
future-gate recommendation is conditional only
all authorization flags are false
claim ceiling remains bounded replay-control adjudication only
```

## Claim Ceiling

Maximum claim:

```text
bounded replay-control adjudication only
```

This cannot prove mechanism validity, 001B pass, theory validity, theory
falsity, Gate1 readiness, bridge readiness, EGO readiness, agency,
consciousness, companion readiness, or model-class reset necessity.

## Rollback Plan

All new files must be isolated to:

```text
artifacts/process_intervention_hard_distribution_001b_trace_replay_rca_001a/
docs/codex/tasks/PROCESS-INTERVENTION-HARD-DISTRIBUTION-001B-TRACE-REPLAY-RCA-001A.md
tests/test_process_intervention_hard_distribution_001b_trace_replay_rca_001a.py
```

If overreach occurs, remove only these new RCA files.
