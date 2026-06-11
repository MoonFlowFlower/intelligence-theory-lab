# GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001A-AMENDMENT-001-TRACE-REPLAY-CONTRACT-PATCH

Task ID: GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001A-AMENDMENT-001-TRACE-REPLAY-CONTRACT-PATCH

Layer: bounded Gate1 task-card amendment only

Base task-card anchor: GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001A at commit `b813651`

Independent audit anchor: GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001B-INDEPENDENT-AUDIT at commit `4e3e9f2`

Verdict:

```text
gate1_task_card_001a_amendment_001_trace_replay_contract_patch_pass
```

## Problem Definition

001B failed the 001A task card because the trace/replay contract did not
explicitly require replay boundary state hashes or a deterministic
replay/consolidation-to-later-behavior linkage key. This amendment patches only
that ambiguity.

This amendment is an overlay on top of 001A at `b813651`. It does not rewrite
the base 001A task-card artifact. It does not rewrite the 001B audit. 001B
failed audit verdict remains historical evidence.

001B failed audit verdict remains historical evidence.

## Patch Scope

The effective future Gate1 task-card contract is:

```text
GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001A at b813651
+ AMENDMENT-001 trace/replay contract overlay
```

Gate1 execution is not authorized. Gate1 runtime implementation is not
authorized. Bridge, EGO mainline, mechanism tournament, and model-class reset
work are not authorized.

## Required Trace / Replay Fields

Future Gate1 execution artifacts must include:

```text
replay_event_id
consolidation_event_id
source_experience_ids
target_case_id
replay_start_time_or_step
replay_end_time_or_step
state_hash_before_replay
state_hash_after_replay
consolidation_state_hash_before
consolidation_state_hash_after
later_behavior_eval_id
replay_to_behavior_linkage_key
linkage_key_derivation_rule
linkage_key_uniqueness_check
linkage_key_collision_report
replay_event_to_later_behavior_join_table
hash_freeze_before_later_behavior_evaluation
mutation_check_after_later_behavior_evaluation
```

This resolves the two 001B blockers:

```text
pre_post_replay_state_traces
replay_to_behavior_linkage
```

## Linkage Key Rule

The `replay_to_behavior_linkage_key` must be deterministic, predeclared, and
frozen before execution and before later behavior evaluation.

Example formula:

```text
sha256(gate1_run_id + target_case_id + replay_event_id + consolidation_event_id + later_behavior_eval_id)
```

The exact formula may differ in a later authorized execution task, but it must
be frozen before execution and must use only predeclared non-target-leaking
fields.

Allowed formula inputs:

```text
gate1_run_id
target_case_id
replay_event_id
consolidation_event_id
later_behavior_eval_id
```

Forbidden formula inputs:

```text
heldout_outcome
target_heldout_outcome
future_behavior_label
target_future_behavior_label
witness_result
witness_match_result
post_evaluation_metric
post_evaluation_metrics
```

The future execution must include a uniqueness check and collision report for
all linkage keys.

## Required Future Execution Artifacts

If Gate1 execution is later authorized, it must emit:

```text
replay_event_log.json
consolidation_trace.json
state_hash_chain.json
replay_behavior_linkage_table.json
linkage_key_collision_report.json
later_behavior_evaluation.json
mutation_check_report.json
```

The linkage table must join replay/consolidation events to later behavior
evaluation records without using heldout outcomes, future behavior labels,
witness results, or post-evaluation metrics as key material.

## Leakage Controls

The linkage key derivation rule must be hash/frozen before later behavior
evaluation. After later behavior evaluation, the run must emit a mutation check
report showing that the frozen derivation rule, replay event log,
consolidation trace, state hash chain, and linkage table were not rewritten.

The linkage key cannot include target heldout outcome, future behavior label,
witness result, or post-evaluation metric fields.

## Authorization

This amendment resolves only the named trace/replay contract ambiguity. It does
not authorize Gate1 execution, Gate1 implementation, executable preflight,
bridge work, EGO mainline work, mechanism validity claims, agency claims,
consciousness claims, or companion readiness claims.

## Claim Ceiling

```text
bounded Gate1 task-card trace/replay contract amendment only
```

This cannot prove Gate1 pass, Gate1 execution readiness beyond resolving this
blocker, mechanism validity, theory validity, bridge readiness, EGO readiness,
agency, consciousness, emotion, companion readiness, or stable user benefit.

## Rollback Plan

If this amendment mutates 001B audit artifacts, rewrites 001B failed verdict as
pass, executes Gate1, implements runtime, adds mechanism code, expands baseline
taxonomy, or authorizes bridge/EGO/model-class reset, stop and revert only this
amendment package.

The amendment package is limited to:

```text
docs/codex/tasks/GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001A-AMENDMENT-001-TRACE-REPLAY-CONTRACT-PATCH.md
tests/test_gate1_task_card_001a_amendment_001_trace_replay_contract_patch.py
artifacts/gate1_task_card_001a_amendment_001_trace_replay_contract_patch/
```
