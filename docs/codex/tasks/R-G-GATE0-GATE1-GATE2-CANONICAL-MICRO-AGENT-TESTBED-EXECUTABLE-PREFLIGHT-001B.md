# R-G-GATE0-GATE1-GATE2-CANONICAL-MICRO-AGENT-TESTBED-EXECUTABLE-PREFLIGHT-001B

Task ID: R-G-GATE0-GATE1-GATE2-CANONICAL-MICRO-AGENT-TESTBED-EXECUTABLE-PREFLIGHT-001B

Layer: bounded canonical micro-agent integration executable preflight only.

Parent anchors:

```text
Gate0 frozen bounded predictive-action / action-conditioned update evidence
Gate1 replay/consolidation executable preflight commit: 6b362e0
Gate2 controllability/self-boundary executable preflight commit: 7046d6f
Micro-agent testbed task card commit: 7ce7887
```

This task may implement and execute only the isolated 001B preflight under the
paths listed below. It does not authorize Gate3, bridge, EGO mainline,
companion, emotion, relationship, LLM/RAG, user-model, deployment, or runtime
integration work.

## Authorized Paths

```text
docs/codex/tasks/R-G-GATE0-GATE1-GATE2-CANONICAL-MICRO-AGENT-TESTBED-EXECUTABLE-PREFLIGHT-001B.md
src/r_g_gate0_gate1_gate2_canonical_micro_agent_testbed_001b/
tests/test_r_g_gate0_gate1_gate2_canonical_micro_agent_testbed_001b_executable.py
artifacts/r_g_gate0_gate1_gate2_canonical_micro_agent_testbed_001b/
```

## Problem Definition

Execute a minimal target-position micro-agent preflight that integrates Gate0
action-conditioned predictive update, Gate1 replay/consolidation-to-later
behavior linkage, and Gate2 controllability/self-boundary update inside one
observe-predict-act-update-replay-boundary loop.

The primary failure mode is a stitched system that combines three separate gate
outputs after the fact. This preflight must fail if the trace cannot show one
shared state schema and one shared state hash lineage from Gate0 through Gate1,
Gate2, and later action selection.

## Hypothesis

If one canonical shared state loop can combine action-conditioned prediction
error, replay/consolidation, controllability error, self-boundary update, and
later action selection while remaining baseline-distinguishable,
ablation-sensitive, leakage-clean, replayable, and bounded by the claim ceiling,
then it may provide bounded executable preflight evidence for integrated
micro-agent testbed readiness.

## Required Loop

```text
observe()
predict_outcome()
select_action()
apply_action()
observe_effect()
compute_prediction_error()
update_belief_state()
replay_or_consolidate()
update_self_boundary_state()
select_later_action()
emit_hash_chained_trace()
```

## Shared State Contract

The executable must use exactly one canonical shared state schema containing:

```text
belief_state
prediction_error_state
replay_memory
consolidation_state
controllability_model
self_boundary_state
action_policy_state
resource_budget_state
```

Gate0 must mutate belief or prediction-error state. Gate1 must mutate replay
memory or consolidation state. Gate2 must mutate controllability or
self-boundary state. Later action selection must read the state after all three
updates.

## Required Baselines

```text
isolated Gate0-only policy
isolated Gate1-only replay policy
isolated Gate2-only controllability policy
stitched-output baseline with no shared state
retrieval / summary retrieval
count/statistic table
transition table / successor map / graph cache
behavior-only imitation
frozen-memory model
frozen-controllability model
random policy
oracle environment-label control as upper-bound/leakage only
trace-only replay as hygiene only
```

The graph/cache family must include graph_lookup, transition_table,
successor_map, count_table, fsm_planner, and episodic_traversal. Oracle and
trace-only replay controls are not fair baselines.

## Required Ablations

```text
remove Gate0 update
remove Gate1 replay/consolidation
remove Gate2 boundary update
freeze shared state
replace shared state history
disable action
invert control mapping
remove controllability feedback
remove replay event
perturb environment
delayed effect
partial observability
heldout action-object compositions
counterfactual action contrast
```

## Required Artifacts

Artifacts must be written only under:

```text
artifacts/r_g_gate0_gate1_gate2_canonical_micro_agent_testbed_001b/
```

Required files:

```text
stage0_freeze_manifest.json
execution_manifest.json
execution_manifest.sha256
run_ledger.jsonl
trace.jsonl
shared_state_trace.jsonl
linkage_report.json
later_behavior_evaluation.json
baseline_comparison.json
ablation_report.json
leakage_report.json
replay_integrity_report.json
mutation_check_report.json
result.json
claim_ceiling.txt
failure_manifest.json if failed
```

## Acceptance Gate

Pass only if Gate0, Gate1, and Gate2 mechanisms remain traceable through one
shared state loop; required baselines do not fairly match or beat the candidate;
the stitched-output baseline does not explain the result; ablations are
sensitive; linkage keys are deterministic, label-free, and collision-free;
leakage is clean; replay integrity passes; and mutation checks pass.

## Claim Ceiling

```text
bounded Gate0/Gate1/Gate2 canonical micro-agent testbed executable preflight evidence only
```

This cannot prove mechanism validity, theory validity, agency, selfhood,
consciousness, real autonomy, bridge readiness, EGO readiness, companion
readiness, or stable user benefit.

## Stop Conditions

Stop and emit failure artifacts if any required baseline fairly matches or
beats the candidate, stitched output explains the result, any required ablation
is insensitive, leakage is detected, linkage keys collide or use labels, trace
or shared-state replay fails, mutation is detected after evaluation, or the
implementation requires a second hidden state path.

## Rollback Plan

Rollback is deletion or exclusion of only the 001B authorized paths. Do not
modify or patch old Gate0, Gate1, Gate2, bridge, EGO, companion, emotion,
relationship, LLM/RAG, user-model, or previous artifact paths to make this
preflight pass.
