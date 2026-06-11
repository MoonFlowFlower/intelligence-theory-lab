# PROCESS-INTERVENTION-FAILURE-RCA-001A Task Card

Task ID: PROCESS-INTERVENTION-FAILURE-RCA-001A

Layer: bounded failure attribution only.

## Problem Definition

Classify why `PROCESS-INTERVENTION-PREFLIGHT-001B` failed when fair controls
matched the witness under frozen support-pack contracts.

This task does not rerun, repair, reinterpret, or upgrade 001B. It only reads
completed 001B failure artifacts and emits a bounded RCA artifact.

## Current Stage

Post-failure RCA over frozen predecessor evidence.

Frozen predecessor inputs:

```text
artifacts/process_intervention_preflight_001b/result.json
artifacts/process_intervention_preflight_001b/failure_manifest.json
artifacts/process_intervention_preflight_001b/control_comparison.json
artifacts/process_intervention_preflight_001b/baseline_comparison.json
artifacts/process_intervention_preflight_001b/replay_report.json
artifacts/process_intervention_preflight_001b/trace.jsonl
artifacts/process_intervention_preflight_001b/frozen_inputs.json
artifacts/process_intervention_preflight_001a_amendment_001_support_pack_001/support_pack_result.json
artifacts/process_intervention_preflight_001a_amendment_001_support_pack_001/support_pack_matrix.json
artifacts/process_intervention_preflight_001a_amendment_001_support_pack_001/support_pack_manifest.json
artifacts/process_intervention_preflight_001a_amendment_001_support_pack_001/support_pack_gate_status.json
```

## Hypothesis

Primary RCA hypothesis:

```text
H1 = 001B failed primarily because the task distribution and frozen metric
surface allowed statistic/count, graph/cache, and trace replay controls to
match intervention response, update-trace proxy, later behavior, and the
separation statistic.
```

Plausible alternatives:

```text
H2 = the witness implementation was underpowered relative to the process
intervention claim.

H3 = the evidence gate mixed implementation/output equivalence with a stronger
state-process claim, making the gate too weak to distinguish mechanism from
shortcut.
```

Null:

```text
H0 = 001B artifacts do not contain enough evidence to classify beyond
mixed_or_ambiguous.
```

## Baseline

The RCA baseline is the frozen 001B failure verdict:

```text
process_intervention_preflight_001b_failed_control_separation_statistic_match
```

The RCA must not replace that verdict. It must use the matched fair controls
as negative evidence.

## Ablation

No new mechanism ablation is authorized. RCA-only ablation means classifying
which already-observed equivalence channels explain the failure:

```text
behavior-level equivalence
state-delta or update-trace equivalence
intervention-response equivalence
statistic/count shortcut
```

## Trace / Replay Requirement

Read the frozen 001B replay and trace artifacts. Do not regenerate predecessor
trace artifacts. Do not treat schema-only replay as mechanism evidence.

## Acceptance Gate

This task passes only if:

```text
RCA artifact is JSON-parseable
old 001B artifacts remain unchanged
authorization flags are all false
result states the most likely failure class and at least one plausible alternative
result defines what evidence would distinguish reset vs implementation revision vs harder task distribution
claim ceiling remains bounded failure attribution only
```

## Claim Ceiling

Maximum claim:

```text
bounded process-intervention 001B failure attribution only
```

This does not prove mechanism validity, theory validity, theory falsity, Gate1
readiness, bridge readiness, EGO readiness, agency, consciousness, or companion
readiness.

## Stop Conditions

Stop if any of these would be required:

```text
authorizing Gate1
authorizing same-agent bridge
authorizing EGO mainline
authorizing model-class reset
implementing a new mechanism
changing thresholds to make 001B pass
reinterpreting failed evidence as success
modifying old 001B artifacts
rewriting support-pack evidence
```

## Rollback Plan

If scope is violated, remove only newly created
`PROCESS-INTERVENTION-FAILURE-RCA-001A` files. Preserve all old 001B and
support-pack artifacts unchanged.
