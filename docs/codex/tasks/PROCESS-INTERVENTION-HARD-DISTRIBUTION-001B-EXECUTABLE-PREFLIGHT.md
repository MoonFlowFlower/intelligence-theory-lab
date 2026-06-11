# PROCESS-INTERVENTION-HARD-DISTRIBUTION-001B Executable Preflight Task Card

Task ID: PROCESS-INTERVENTION-HARD-DISTRIBUTION-001B-EXECUTABLE-PREFLIGHT

Layer: bounded hard-distribution process-intervention executable preflight only.

## Problem Definition

`PROCESS-INTERVENTION-FAILURE-RCA-001A` classified the 001B failure as most
likely `task_distribution_weak`. `PROCESS-INTERVENTION-HARD-DISTRIBUTION-001A`
froze a harder process-intervention distribution with observable-key conflicts,
delayed effects, partial observability, heldout compositions, counterfactual
action pairs, and ablation hooks.

This task executes a bounded preflight on that frozen hard distribution to test
whether the current process-intervention witness still collapses to fair
count/statistic/cache/replay/retrieval controls.

## Current Stage

No Gate1 authorization. No bridge authorization. No EGO mainline authorization.
No model-class reset authorization. No mechanism tournament authorization. No
companion, emotion, relationship, or user-model module authorization.

## Hypothesis

If the 001B collapse was primarily caused by weak task distribution, then the
frozen hard distribution should reduce or eliminate perfect fair-control
equivalence while preserving replay, intervention, and ablation auditability.
If fair controls still match at `1.0`, the current process-intervention evidence
remains negative or ambiguous.

## Baseline

`PROCESS-INTERVENTION-PREFLIGHT-001B` collapsed to fair controls at:

```text
match_rate = 1.0
update_trace_match_rate = 1.0
later_behavior_match_rate = 1.0
separation_margin = 0.0
```

## Frozen Inputs

Use only the frozen artifacts from
`PROCESS-INTERVENTION-HARD-DISTRIBUTION-001A`:

```text
hard_distribution_spec.json
frozen_inputs.json
distribution_shortcut_audit.json
fair_control_budget_spec.json
heldout_composition_manifest.json
ablation_hook_manifest.json
```

## Required Actions

1. Verify frozen input hashes before execution.
2. Run the process-intervention witness on the hard distribution.
3. Run all predeclared fair controls under the same access budget:

```text
online_count_statistic
count_table
graph_cache
transition_table
successor_map
trace_only_replay
behavior_only_replay
summary_retrieval
```

4. Evaluate intervention-response match, update-trace/process metric, later
behavior change, heldout composition performance, delayed-effect performance,
observable-key conflict cases, and partial-observability cases.
5. Run predeclared ablations: learning freeze, history replacement, and
counterfactual action contrast. Outcome perturbation is skipped unless already
declared by 001A.
6. Produce machine-readable artifacts under:

```text
artifacts/process_intervention_hard_distribution_001b/
```

## Required Artifacts

```text
result.json
control_comparison.json
baseline_comparison.json
ablation_report.json
replay_report.json
heldout_report.json
failure_manifest.json if failed
claim_ceiling.txt
```

## Negative Checks

Fail if any fair control matches the witness at the predeclared equivalence
threshold, trace-only replay is treated as mechanism evidence, heldout
compositions are missing or evaluated post hoc, ablation hooks are not
executed, learning-freeze or history-replacement does not change expected
process-sensitive behavior, thresholds are changed after seeing results, old
001B/RCA artifacts are edited, hard-distribution 001A frozen artifacts are
modified, or Gate1/bridge/EGO/model-class reset/mechanism tournament becomes
authorized.

## Acceptance Gate

Pass only if:

```text
frozen input hashes match 001A
witness executes on the hard distribution
fair controls execute under predeclared budgets
no fair control matches the witness under frozen equivalence criteria
replay report is valid but not treated as sufficient mechanism evidence
ablation results show process-sensitive degradation/change in the predicted direction
heldout composition report exists
observable-key conflict cases are evaluated separately
JSON artifacts are parseable
authorization flags are all false
claim ceiling remains bounded hard-distribution process-intervention evidence only
```

## Failure Verdicts

```text
process_intervention_hard_distribution_001b_failed_fair_control_match
process_intervention_hard_distribution_001b_failed_witness_underpowered
process_intervention_hard_distribution_001b_invalid_execution_leakage_or_freeze_violation
process_intervention_hard_distribution_001b_bounded_pass
```

## Claim Ceiling

Maximum claim:

```text
bounded hard-distribution process-intervention preflight evidence only
```

This cannot prove theory validity, theory falsity, Gate1 readiness, bridge
readiness, EGO readiness, agency, consciousness, real emotion, companion
readiness, or model-class reset necessity.

## Rollback Plan

All execution code and artifacts are isolated to
`PROCESS-INTERVENTION-HARD-DISTRIBUTION-001B` paths. If overreach occurs, revert
only the 001B execution commit.
