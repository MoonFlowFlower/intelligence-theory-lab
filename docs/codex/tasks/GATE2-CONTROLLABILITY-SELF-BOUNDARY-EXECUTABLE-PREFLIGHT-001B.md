# GATE2-CONTROLLABILITY-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001B

Task ID: GATE2-CONTROLLABILITY-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001B

Layer: bounded Gate2 executable preflight only.

Parent task-card anchor:

```text
GATE2-CONTROLLABILITY-SELF-BOUNDARY-TASK-CARD-001A
parent_commit = 76a20d9
parent_path = docs/codex/tasks/GATE2-CONTROLLABILITY-SELF-BOUNDARY-TASK-CARD-001A.md
```

The parent task card is read-only for this task.

## Authorization Boundary

Authorized isolated paths:

```text
docs/codex/tasks/GATE2-CONTROLLABILITY-SELF-BOUNDARY-EXECUTABLE-PREFLIGHT-001B.md
src/gate2_controllability_self_boundary_001b/
tests/test_gate2_controllability_self_boundary_001b_executable.py
artifacts/gate2_controllability_self_boundary_001b/
```

Forbidden:

```text
old Gate0 artifacts
old Gate1 artifacts
old process-intervention artifacts
old representational-gap artifacts
bridge work
EGO mainline
companion behavior
emotion / relationship / user-model modules
LLM / RAG integration
mechanism tournament
claim inflation
```

## Problem Definition

Execute an isolated Gate2 preflight testing whether a bounded offline system can
maintain an action-conditioned controllability / self-boundary proxy, update it
under observed effects and perturbations, and use that updated state to select
later actions on heldout action-object compositions.

## Hypothesis

If a compositional controllability model predicts self-controllable versus
externally caused state changes, updates its self-boundary state from observed
effects, changes later action selection through a label-free linkage key, and
remains distinguishable from fair retrieval/table/cache/imitation/frozen/random
controls under a frozen contract, then this run may support bounded Gate2
controllability / self-boundary executable preflight evidence.

## Baselines

Required baselines:

```text
retrieval / summary retrieval
identity-tag lookup
actor-id table
action-outcome count table
transition table / successor map / graph cache
behavior-only imitation
trace-only replay as hygiene only
frozen-controllability model
random-action policy
oracle environment-label control
```

Graph-cache family variants:

```text
graph_lookup
transition_table
successor_map
count_table
fsm_planner
episodic_traversal
```

Trace-only replay is hygiene only. Oracle environment-label control is a
leakage / upper-bound control only.

## Ablations

Required ablations:

```text
action disabled
control mapping inverted
controllability feedback removed
history replacement
learning freeze
environment perturbation
delayed controllability effect
partial observability
heldout action-object compositions
counterfactual action contrast
```

## Required Artifacts

All execution artifacts must be written under:

```text
artifacts/gate2_controllability_self_boundary_001b/
```

Required artifacts:

```text
stage0_freeze_manifest.json
sha256_manifest.json
external_anchor.json
prediction_commit.json
prediction_commit.sha256
access_log.json
trace.jsonl
controllability_error_report.json
self_boundary_update_report.json
later_action_linkage_report.json
later_behavior_evaluation.json
leakage_report.json
baseline_comparison.json
control_comparison.json
ablation_report.json
replay_report.json
mutation_check_report.json
result.json
claim_ceiling.txt
execution_manifest.json
execution_manifest.sha256
run_ledger.jsonl
final_report.md
failure_manifest.json if failed
```

## Acceptance Gate

Pass only if all are true:

```text
Stage 0 freeze exists before candidate/control runs
prediction commit is hash-frozen before target reveal
candidate shows bounded action-conditioned controllability evidence
candidate links self-boundary updates to later action selection
no fair non-oracle baseline matches or beats the candidate
trace-only replay remains hygiene only
oracle environment-label control remains leakage/upper-bound only
all required ablations are sensitive
leakage scan passes
linkage keys are label-free and collision-free
mutation check after evaluation passes
authorization flags remain false
claim ceiling remains bounded executable preflight evidence only
```

## Allowed Verdicts

```text
gate2_controllability_self_boundary_001b_bounded_preflight_pass
gate2_controllability_self_boundary_001b_failed_baseline_match
gate2_controllability_self_boundary_001b_failed_ablation_insensitive
gate2_controllability_self_boundary_001b_failed_trace_contract
gate2_controllability_self_boundary_001b_invalid_leakage
gate2_controllability_self_boundary_001b_invalid_mutation
gate2_controllability_self_boundary_001b_failed_stage0_freeze
```

## Claim Ceiling

Maximum claim:

```text
bounded Gate2 controllability / self-boundary executable preflight evidence only
```

This does not prove selfhood, agency, consciousness, real autonomy, mechanism
validity, theory validity, bridge readiness, EGO readiness, companion
readiness, or stable user benefit.

## Rollback Plan

If the run fails, preserve failure artifacts and do not patch forward
automatically. If scope leaks, revert only the isolated 001B paths listed
above and leave all old artifacts untouched.
