# PROCESS-INTERVENTION-HARD-DISTRIBUTION-001A Task Card

Task ID: PROCESS-INTERVENTION-HARD-DISTRIBUTION-001A

Layer: bounded process-intervention task-distribution hardening only.

## Problem Definition

`PROCESS-INTERVENTION-FAILURE-RCA-001A` classified the 001B failure as most
likely `task_distribution_weak`. The 001B distribution collapsed because fair
count/statistic, graph-cache, and replay controls matched a small,
deterministic, conflict-free observable key surface.

This task freezes a harder distribution contract that removes that shortcut
structure without weakening fair controls, changing thresholds, editing old
failed evidence, authorizing Gate1, authorizing a bridge, touching EGO, or
implementing a new mechanism.

## Current Stage

Distribution-readiness freeze only.

No executable mechanism, verifier run, training, model-class reset, Gate1
reopen, bridge work, EGO integration, or threshold change is authorized.

## Hypothesis

A harder frozen distribution with hidden/history-dependent effects, heldout
intervention compositions, delayed consequences, partial observability, and
observable-key conflicts can test whether a future process-intervention
candidate survives beyond count/statistic/cache/replay shortcuts.

This task only prepares that harder distribution surface. It does not test or
prove the hypothesis.

## Baseline

Baseline negative evidence:

```text
PROCESS-INTERVENTION-PREFLIGHT-001B collapsed to fair controls at match_rate=1.0.
PROCESS-INTERVENTION-FAILURE-RCA-001A classified the most likely failure class as task_distribution_weak.
```

## Required Distribution Properties

The frozen distribution must include:

```text
same observable context/intervention/action keys with different outcomes
future behavior not directly recoverable from most recent actual observation
delayed intervention consequences
partial observability and ambiguity
heldout intervention compositions
counterfactual action pairs under shared observation history
learning-freeze and history-replacement ablation hooks
frozen inputs before any execution
preserved fair controls and access rules
```

## Required Artifacts

```text
artifacts/process_intervention_hard_distribution_001a/hard_distribution_spec.json
artifacts/process_intervention_hard_distribution_001a/frozen_inputs.json
artifacts/process_intervention_hard_distribution_001a/distribution_shortcut_audit.json
artifacts/process_intervention_hard_distribution_001a/fair_control_budget_spec.json
artifacts/process_intervention_hard_distribution_001a/heldout_composition_manifest.json
artifacts/process_intervention_hard_distribution_001a/ablation_hook_manifest.json
artifacts/process_intervention_hard_distribution_001a/claim_ceiling.txt
```

## Fair Controls

Fair controls must remain preserved and predeclared:

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

Controls may use the same observable context, intervention condition, action,
history, and trace fields as a future candidate, within budget. Controls may
not use future outcomes, hidden-state labels, verifier labels, or post-hoc
split labels.

## Acceptance Gate

Pass only if:

```text
new distribution is frozen before any execution
deterministic key-conflict audit confirms shortcut-breaking conflicts exist
heldout intervention composition split exists
delayed-effect cases exist
partial-observability cases exist
fair control budget and access rules are predeclared
ablation hooks are predeclared
JSON artifacts are parseable
authorization flags are all false
claim ceiling remains bounded task-distribution hardening only
```

## Negative Checks

Fail if:

```text
context/intervention/action uniquely determines outcome across the full distribution
future behavior is directly recoverable from actual observation alone
heldout split is missing
delayed effects are missing
fair controls are weakened or removed
scale is increased without structural shortcut removal
thresholds are changed to force a pass
old 001B artifacts are edited
Gate1, bridge, EGO, model-class reset, mechanism implementation, or mechanism training becomes authorized
```

## Claim Ceiling

Maximum claim:

```text
bounded process-intervention hard-distribution readiness only
```

This cannot prove mechanism validity, theory validity, theory falsity, Gate1
readiness, bridge readiness, EGO readiness, agency, consciousness, companion
readiness, or model-class reset necessity.

## Stop Condition

Stop and fail if this task requires implementing or training a new mechanism,
weakening fair controls, modifying old failed evidence, increasing scale
without breaking the count/statistic shortcut, or setting any authorization
flag to true.

## Rollback Plan

If overreach is detected, remove only files under:

```text
artifacts/process_intervention_hard_distribution_001a/
docs/codex/tasks/PROCESS-INTERVENTION-HARD-DISTRIBUTION-001A.md
tests/test_process_intervention_hard_distribution_001a.py
```

Preserve all old 001B and RCA artifacts unchanged.
