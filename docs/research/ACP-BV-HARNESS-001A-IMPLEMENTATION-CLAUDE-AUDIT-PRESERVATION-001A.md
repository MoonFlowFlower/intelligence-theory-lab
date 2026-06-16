# ACP-BV Harness 001A Implementation Claude Audit Preservation 001A

Task id:
`ACP-BV-HARNESS-001A-IMPLEMENTATION-AUDIT-PRESERVATION-AND-FAIR-BASELINE-REPAIR-001A`

Preserved audit target:
`ACP-BV-EXECUTABLE-HARNESS-001A`

Current layer:
engineering implementation / evidence-hygiene repair only.

Mainline integration status: none.

Enabled status: local offline CLI/test runner only.

Real trigger evidence:
the attached hostile implementation audit identified that the 001A
implementation result could not support an ACP-BV mechanism claim because the
baseline matrix was weak or unfair and a fair lookup baseline was sufficient
under the current distribution.

## Preserved External Audit Verdict

Single restricted audit verdict:
`blocked_by_weak_or_unfair_baseline_matrix`

Underlying task-level blocker after fair-baseline repair:
`blocked_by_baseline_equivalence`

The runtime mutation control result
`blocked_by_runtime_mutation_or_temporal_boundary_gap` is preserved as an
expected negative-control block. It is not promoted to the task-level blocker.

## Preserved Findings

- The prior 001A candidate behaved as an oracle-like reference candidate under
  the current scaffolded distribution.
- The prior graph-cache challengers were information-starved relative to the
  candidate and therefore could not support a mechanism-relevant delta.
- A full-access lookup baseline using
  `(signal, topology, risk, action)` reaches `1.0` on the current heldout
  distribution.
- The candidate also reaches `1.0`, so the fair-baseline delta is `0.0`.
- The train and heldout observation-action key sets overlap completely under
  the current distribution.
- The earlier source-pin manifest was self-trusting because it was derived from
  live files at run time.
- No real Gate target, bridge target, admission target, runtime path, or EGO
  mainline path was exercised.

## Repair Readback

The repair adds a fail-able fair-baseline and source-pin control layer without
changing the claim ceiling:

- fair baseline: `full_access_lookup_baseline`
- baseline key schema: `(signal, topology, risk, action)`
- strongest baseline score: `1.0`
- candidate score: `1.0`
- strongest-baseline delta: `0.0`
- B3 classification: `baseline_equivalent`
- train keys: `18`
- heldout keys: `18`
- overlapping keys: `18`
- heldout contains unseen keys: `false`
- memory lookup can be complete policy: `true`
- candidate/truth classification:
  `oracle_like_reference_candidate_scaffolding_only`
- repaired source-pin mode: `git_object_frozen_anchor`

## Claim Ceiling

Maximum claim:
`current_001a_distribution_exposes_baseline_equivalence_or_non_discriminative_surface`

This record preserves negative evidence. It does not prove ACP-BV validity,
ACP-BV mechanism validity, Gate validity, bridge readiness, admission
readiness, runtime readiness, EGO readiness, agency evidence, consciousness,
real emotion, autonomy, stable user benefit, or mainline effect.

## Next Minimal Closed-Loop Action

Do not repair 001A further into a pass-shaped result. Route to a separate
ACP-BV 001B distribution redesign or downgrade the current ACP-BV surface.
