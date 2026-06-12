# EGO-MAINLINE-ADMISSION-EXECUTABLE-001D-METRIC-PROVENANCE-REPAIR-001F

## Task Identity

```text
task_id = EGO-MAINLINE-ADMISSION-EXECUTABLE-001D-METRIC-PROVENANCE-REPAIR-001F
layer = bounded metric-provenance repair rerun for EGO-MAINLINE-ADMISSION-EXECUTABLE-001D only
claim_ceiling = bounded metric-provenance repair evidence for 001D under synthetic / controlled conditions only
```

## Problem Definition

Repair only the exact 001E metric-provenance blocker:

```text
all 12 verdict-bearing 001D metric rows missing train_context_ids_consumed
all 12 verdict-bearing 001D metric rows missing heldout_context_ids_consumed
all 12 verdict-bearing 001D metric rows missing counterfactual_pair_ids_consumed
old_artifact_mutation uses wrapper-only provenance
```

This task does not rewrite old 001B, 001C, 001D, or 001E artifacts. It does not
restore 001B positive evidence status and does not convert the 001E blocker into
a caveat.

The unrelated local theory-landscape/compression stream is outside 001F scope.
If `docs/THEORY-LANDSCAPE-COVERAGE-COMPRESSION-001A.md` or its sibling
`docs/THEORY-LANDSCAPE-COVERAGE-COMPRESSION/` sidecar directory is present, it
must remain unstaged, uncommitted, unread as evidence, and excluded from 001F
artifacts.

## Current Stage

001E is the canonical blocker:

```text
remote_tag = remote-anchor-001t-8ed4a5a
commit = 8ed4a5a602694748fc1407bed4ef1224057b2874
verdict = ego_mainline_admission_executable_001d_independent_audit_001e_block_metric_provenance_gap
```

001D remains a repair candidate blocked by 001E until this 001F result is judged
separately.

## Hypothesis

The exact 001E blocker is repairable if a new 001F rerun can produce per-metric
context-consumption provenance from callable producers and true
old-artifact-mutation producer provenance, while preserving old artifacts and
bounded claims.

## Baseline

The baseline explanation is that 001D already had callable metric provenance for
most rows, but its schema omitted required frozen-context consumption fields and
used wrapper provenance for old artifact mutation.

## Ablation

Corruptions must block:

```text
missing train_context_ids_consumed
missing heldout_context_ids_consumed
missing counterfactual_pair_ids_consumed
empty consumed-context fields when frozen inputs exist
decorative context IDs absent from producer consumption report
wrapper-only old_artifact_mutation provenance
missing before hash
missing after hash
```

## Trace / Replay Requirement

The rerun must emit machine-readable artifacts under:

```text
artifacts/ego_mainline_admission_executable_001d_metric_provenance_repair_001f/
```

Metric rows must be traceable to:

```text
context_consumption_report.json
context_consumption_crosscheck.json
metric_provenance.json
old_artifact_mutation_report.json
old_artifact_mutation_provenance_report.json
```

## Acceptance Gate

Pass only if all acceptance gates in `result.json` are true, including:

```text
parent anchors 001t/001s/001r/001q/001p/001o verified
computed-evidence contract loaded
001E blocker preserved
repair scope exact
old 001D and 001E artifacts not modified
known theory file left unstaged and unmodified
all verdict metrics include train/heldout/counterfactual consumed IDs
context consumption fields computed by callable producers
context consumption crosschecked against freeze
old_artifact_mutation true producer provenance
failure-path controls passed
baseline/ablation/leakage/manual/metadata/replay/frozen/negative checks valid
no scope leak
no claim inflation
```

## Stop Condition

Stop with the most specific blocker if any required parent anchor, context
consumption field, callable producer, old-artifact hash, revalidation, scope, or
claim-ceiling gate fails.

## Rollback Plan

If blocked, preserve the new 001F failure artifacts, do not rewrite old evidence,
do not weaken the computed-evidence contract, do not stage the known theory file,
and repair only the exact new blocker in a later bounded task.

## What This Does Not Prove

This does not prove 001D independent audit pass, 001B independent audit pass,
001B positive evidence restoration, EGO readiness, EGO mainline readiness,
runtime admissibility, bridge readiness, companion readiness, mechanism
validity, theory validity, agency, selfhood, consciousness, real emotion, real
relationship learning, stable user benefit, production readiness, or correctness
of any future EGO runtime.
