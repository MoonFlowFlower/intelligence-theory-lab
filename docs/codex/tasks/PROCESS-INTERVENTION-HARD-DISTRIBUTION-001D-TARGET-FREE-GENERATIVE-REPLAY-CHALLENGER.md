# PROCESS-INTERVENTION-HARD-DISTRIBUTION-001D-TARGET-FREE-GENERATIVE-REPLAY-CHALLENGER Task Card

Task ID: PROCESS-INTERVENTION-HARD-DISTRIBUTION-001D-TARGET-FREE-GENERATIVE-REPLAY-CHALLENGER

Layer: bounded target-free replay challenger preflight only.

## Problem Definition

001C froze a future replay-gate contract at commit `afeff65`, requiring any
target-free generative replay challenger to emit `prediction_commit.json`,
freeze its hash before reveal, and evaluate only after target records are
revealed. 001B / RCA / 001C artifacts are read-only after that anchor.

The current task instantiates that contract as a bounded preflight. It tests
whether a target-free support-only challenger can match the witness evaluation
targets without target leakage.

## Current Stage

Preflight execution only. No Gate1 authorization. No bridge authorization. No
EGO authorization. No model-class reset authorization. No mechanism tournament
authorization. No historical verdict rewrite.

## Anti-Sycophancy Audit

Strongest baseline explanation: a support-only challenger may recover weak
regularities from visible support/prefix fields without representing the
witness update process.

Strongest reason this task may be invalid: if Phase A can read target heldout
labels, target future behavior, target witness trace rows, process signatures,
failure manifests, or control-comparison target results, then the challenger is
not target-free and the preflight must fail.

Falsifier for the current framing: Phase A access log contains any forbidden
target/reveal source, `prediction_commit.sha256` is created after reveal, or
Phase B rewrites `prediction_commit.json`.

Evidence still insufficient: a clean target-free challenger mismatch does not
prove the witness mechanism, Gate1 readiness, bridge readiness, or EGO
readiness.

This task tests a target-free challenger access/evaluation protocol. It does
not test consciousness, agency, selfhood, or companion readiness.

## Hypothesis

If the 001C Phase A/B contract is enforced, a support-only target-free
generative replay challenger can be evaluated without allowing trace-only
replay hygiene to masquerade as mechanism evidence.

## Baseline

Historical 001B failed because `trace_only_replay` matched at 1.0 under the
historical gate. 001B-RCA and 001C reclassified trace-only replay as future
trace hygiene only, while preserving the historical 001B failure verdict.

## Ablation

No new mechanism ablation is introduced. The preflight must preserve the 001B
ablation evidence boundary and report whether witness/ablation prerequisites
remain usable.

## Trace / Replay Requirement

Phase A may read only:

```text
allowed_prefix
support_split
permitted_history
```

Phase A must generate and freeze:

```text
prediction_commit.json
prediction_commit.sha256
access_log.json
```

Phase B may reveal target/evaluation records only after hash verification and
must not rewrite Phase A predictions.

## Required Evaluations

```text
intervention-response match
later behavior match
update/process-signature match
heldout composition cases
delayed-effect cases
observable-key conflict cases
partial-observability cases
```

## Preserved Controls

```text
online_count_statistic
count_table
graph_cache
transition_table
successor_map
behavior_only_replay
summary_retrieval
trace_only_replay as hygiene only
```

## Acceptance Gate

Pass only if:

```text
access firewall is explicit, allowlist-based, and enforced
prediction_commit is frozen before reveal
Phase B cannot rewrite Phase A commit
target-free challenger is evaluated after reveal
trace_only_replay remains hygiene only
existing non-replay fair controls remain preserved
JSON artifacts parse
old 001B / RCA / 001C artifacts remain unchanged from afeff65 onward
all authorization flags remain false
claim ceiling remains bounded target-free replay challenger preflight evidence only
```

## Possible Verdicts

```text
process_intervention_hard_distribution_001d_failed_target_free_replay_challenger_match
process_intervention_hard_distribution_001d_failed_witness_or_ablation
process_intervention_hard_distribution_001d_bounded_replay_gate_pass
process_intervention_hard_distribution_001d_invalid_access_leakage
```

## Stop Condition

Stop and fail if target leakage occurs, prediction commit is not frozen before
reveal, old artifacts are edited, 001B is reclassified as pass, replay hygiene
is treated as mechanism evidence, any authorization flag becomes true, or the
task expands into Gate1 / bridge / EGO / mechanism tournament.

## Claim Ceiling

Maximum claim:

```text
bounded target-free generative replay challenger preflight evidence only
```

This cannot prove mechanism validity, 001B pass, theory validity, theory
falsity, Gate1 readiness, bridge readiness, EGO readiness, agency,
consciousness, companion readiness, or model-class reset necessity.

## Rollback Plan

All changes must be isolated to:

```text
docs/codex/tasks/PROCESS-INTERVENTION-HARD-DISTRIBUTION-001D-TARGET-FREE-GENERATIVE-REPLAY-CHALLENGER.md
src/process_intervention_hard_distribution_001d/
tests/test_process_intervention_hard_distribution_001d_target_free_challenger.py
artifacts/process_intervention_hard_distribution_001d_target_free_generative_replay_challenger/
```

If leakage or overreach is detected, stop and revert only the 001D files.
