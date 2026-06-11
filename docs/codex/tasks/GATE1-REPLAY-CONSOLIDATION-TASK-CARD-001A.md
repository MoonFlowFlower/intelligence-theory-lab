# GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001A

Task ID: GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001A

Layer: bounded Gate1 task-card drafting only

Freeze anchor: PI-HD-ADMISSION-001 at commit `6a83b9d`

This is not Gate1 execution. This is not bridge work. This is not EGO mainline
work. This is not mechanism tournament work. This is not a model-class reset.

## Problem definition

Draft a bounded Gate1 task card for replay / consolidation evidence using only
the admitted process-intervention hard-distribution lineage as upstream
evidence. The card defines a future falsifiable execution plan, but does not
execute Gate1, implement Gate1 runtime, add mechanism code, or mutate old
Gate0, 001B, RCA, 001C, 001D, or admission artifacts.

Strongest baseline explanation: later behavior may be explained by retrieval,
summary retrieval, trace replay hygiene, count/statistic controls, transition
tables, successor maps, graph caches, frozen histories, or behavior-only
imitation without any consolidation mechanism.

Strongest reason this task may be invalid: the admission at `6a83b9d`
authorizes only drafting. If this task reads target outcomes as if evaluating
Gate1, reuses old Gate1 execution artifacts as new evidence, implements a new
runtime, or treats 001D challenger mismatch as witness performance, the task is
invalid.

Falsifier for the current framing: any old artifact mutation, any Gate1
execution side effect, any positive execution authorization flag, missing
required baseline family, missing required ablation, or claim stronger than
task-card readiness.

Evidence still insufficient: a complete task card cannot prove Gate1 pass,
mechanism validity, theory validity, bridge readiness, EGO readiness, agency,
consciousness, emotion, companion readiness, or stable user benefit.

This artifact tests task-card completeness and boundary discipline. It does
not test the mechanism itself.

## Current stage

Gate1 task-card drafting is admitted by PI-HD-ADMISSION-001 at commit
`6a83b9d`. Gate1 execution is not authorized. Gate1 implementation is not
authorized. Bridge work is not authorized. EGO mainline work is not authorized.
Mechanism tournament work is not authorized. Model-class reset is not
authorized.

Historical 001B remains failed. 001D did not rewrite 001B. Trace-only replay
remains hygiene only. The target-free generative replay challenger metrics are
challenger match metrics, not witness performance metrics.

## Hypothesis

A valid Gate1 replay / consolidation execution plan should test whether
process-intervention-relevant update traces can be retained, replayed,
consolidated, and made to affect later behavior under controlled heldout and
shifted conditions, while remaining distinguishable from retrieval, trace-only
replay, count/statistic controls, graph or transition controls, frozen-history
controls, and behavior-only imitation.

## Baseline families

The future Gate1 execution task must compare against all of these families:

```text
retrieval / summary retrieval
behavior-only replay
trace-only replay as hygiene only
online count/statistic controls
transition table / successor map / graph cache controls
target-free generative replay challenger
frozen-history control
no-consolidation control
shuffled-replay control
corrupted-replay control
```

Trace-only replay is permitted only as trace-integrity hygiene. It cannot count
as mechanism evidence and cannot rescue a mechanism claim.

This task card names required future baseline families only. It does not add
new executable baselines, change old baseline artifacts, or add a new replay
taxonomy.

## Ablations

The future Gate1 execution task must include all of these ablations:

```text
learning freeze
history replacement
consolidation disabled
replay order shuffled
replay content corrupted
heldout composition
delayed-effect cases
observable-key conflict cases
partial-observability cases
counterfactual action contrast
```

The expected signal is not merely lower score. The report must show whether the
specific process-intervention-relevant update trace, consolidation step, and
later behavior effect changed in the expected direction under each ablation.

## Trace / replay requirement

Future Gate1 execution must predeclare an execution manifest before target
reveal. The manifest must include the allowed input set, split definitions,
schema hashes, baseline list, ablation list, metric definitions, artifact list,
stop conditions, and claim ceiling. Its hash must be frozen before any heldout
outcome, target future behavior, target process signature, or target evaluation
label is read.

Required future execution artifacts:

```text
result.json
run_ledger.jsonl
access_log.json
trace.jsonl
execution_manifest.json
execution_manifest.sha256
consolidation_report.json
baseline_comparison.json
ablation_report.json
replay_report.json
heldout_report.json
leakage_audit.json
failure_manifest.json when anything fails
claim_ceiling.txt
final_report.md
```

Trace records must preserve input observation, action, update event, replay
event, consolidation event, state hash before update, state hash after update,
state hash after consolidation, allowed source lineage, and later behavior
query. Replay must reconstruct the allowed update path from frozen traces and
must verify that Phase B evaluation did not rewrite Phase A or manifest data.

## Access and leakage controls

Before reveal, future Gate1 execution may read only explicitly allowlisted
support, prefix, schema, permitted history, and frozen upstream evidence from
the admitted process-intervention hard-distribution lineage.

Before reveal, it must not read:

```text
target heldout outcomes
target future behaviors
witness trace rows for target cases
process signatures for target cases
post-ablation target results
failure manifests for target cases
control-comparison target results
old Gate1 execution artifacts as new evidence
```

Access must be allowlist-based, logged, and machine-checkable. The future run
must fail if labels leak through filenames, observable keys, action names,
fixture names, process-signature hashes, split names, cached summaries, or
target trace row ordering.

Phase B may reveal target/evaluation records only after the manifest hash is
frozen. Phase B must not rewrite pre-reveal predictions, pre-reveal traces, or
the execution manifest.

## Acceptance gate

This task-card drafting task passes only if the drafted card defines a
falsifiable Gate1 execution plan with explicit baselines, ablations,
trace/replay requirements, leakage controls, artifact requirements, verdict
set, claim ceiling, stop conditions, and rollback plan.

The drafted card must preserve this verdict set:

```text
gate1_replay_consolidation_task_card_001a_bounded_pass
gate1_replay_consolidation_task_card_001a_failed_scope_leak
gate1_replay_consolidation_task_card_001a_failed_missing_baselines
gate1_replay_consolidation_task_card_001a_failed_missing_ablations
gate1_replay_consolidation_task_card_001a_failed_claim_inflation
gate1_replay_consolidation_task_card_001a_invalid_artifact_mutation
```

A later Gate1 execution task is not authorized by this card. It must be
separately authorized before running and must preserve the access firewall,
manifest freeze, required baselines, required ablations, trace/replay
requirements, and claim ceiling defined here.

## Claim ceiling

The maximum claim is:

```text
bounded Gate1 replay/consolidation task-card readiness only
```

This supports only readiness to draft a bounded Gate1 replay/consolidation task
card. It does not support Gate1 pass, mechanism validity, theory validity,
bridge readiness, EGO readiness, agency, consciousness, emotion, companion
readiness, or stable user benefit.

## Stop conditions

Stop and fail if any of the following occur:

```text
the task expands into Gate1 execution
the task implements Gate1 runtime
the task adds new mechanism code
old Gate0, 001B, RCA, 001C, 001D, or admission artifacts are modified
001B is rewritten or reclassified as pass
trace-only replay is treated as mechanism evidence
Gate1 execution or implementation is authorized
bridge, EGO, mechanism tournament, or model-class reset work is authorized
the claim ceiling is upgraded beyond task-card drafting readiness
required baseline families are missing
required ablations are missing
JSON artifacts do not parse
```

## Rollback plan

Rollback is limited to the new files for this task:

```text
docs/codex/tasks/GATE1-REPLAY-CONSOLIDATION-TASK-CARD-001A.md
tests/test_gate1_replay_consolidation_task_card_001a.py
artifacts/gate1_replay_consolidation_task_card_001a/
```

Do not revert or edit old Gate0, 001B, RCA, 001C, 001D, admission, or existing
Gate1 execution artifacts. If scope leak or artifact mutation is detected,
discard only this task's new files and report the failed verdict.

## Non-claims

This task card cannot prove:

```text
Gate1 pass
mechanism validity
theory validity
bridge readiness
EGO readiness
agency
consciousness
emotion
companion readiness
stable user benefit
```
