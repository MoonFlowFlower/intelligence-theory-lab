# ACP-BV Distribution Redesign Spec 001B Claude Audit 001A

Task id: `ACP-BV-001B-REDESIGN-SPEC-R1-R5-REVISION-001A`

Preservation status: hostile spec audit preserved for bounded spec revision.

## Layer And Status

Current layer: mechanism-hypothesis / engineering-governance 001B redesign
spec revision only.

Mainline integration status: none.

Enabled status: none. This preservation record creates no Gate, bridge,
runtime, admission path, scheduler, live path, mainline path, or real Gate
target.

Real trigger evidence:

- Starting commit:
  `b34d74a892333b4b47962a941866887851d503dd`
- Starting tag:
  `remote-anchor-acp-bv-001a-baseline-equivalence-closure-001b-redesign-spec-001a-b34d74a`
- Prior verdict:
  `acp_bv_001a_closed_and_001b_redesign_spec_ready_for_independent_audit`
- Claude hostile spec audit verdict:
  `requires_001b_spec_revision_before_implementation_card`

Claim ceiling: ACP-BV 001B distribution redesign spec R1-R5 revision only.

Next minimal closed-loop action: send the revised
`docs/research/ACP-BV-DISTRIBUTION-REDESIGN-SPEC-001B.md` for targeted
independent re-audit of R1-R5 before any ACP-BV 001B implementation card is
drafted.

## Preserved Claude Verdict

Claude found that all ten required spec elements were present, but the decision
rules still permitted baseline equivalence to recur under a renamed or
thin-tail distribution.

Preserved verdict:

```text
requires_001b_spec_revision_before_implementation_card
```

Implementation remains unauthorized. This audit preservation and revision task
does not implement ACP-BV 001B and does not authorize `src/**`, `tests/**`,
Gate, bridge, runtime, admission, mainline, scheduler, live, or real Gate
target changes.

## Ten Elements Present Before Revision

Claude accepted presence of these ten required elements at the spec-structure
level:

1. true heldout generalization;
2. fair full-access lookup baseline from the start;
3. strongest-baseline selection after execution;
4. candidate/truth formula-coupling prevention;
5. B3 bands;
6. independent solvability preflight;
7. memory-resistance mechanism targeting lookup;
8. no candidate-authored truth;
9. source-boundary and git-object source-pin carryover;
10. one-redesign Anti-Zeno rule.

This presence finding did not make the spec implementation-ready, because the
required decision rules were still too weak.

## Required Revisions

### R1 - Baseline Equivalence Trigger And Novelty Floor

Required revision: generalize the baseline-equivalence blocker beyond
`overlap_ratio == 1.0`; require a predeclared heldout novelty floor; persist
train/heldout key counts, exact overlap, unseen-heldout metrics,
factorized/per-component seen ratio, novelty threshold, novelty-floor verdict,
fair memory/lookup/nearest-neighbor tie status, and B3 classification.

Required blockers:

```text
blocked_by_insufficient_heldout_novelty
blocked_by_baseline_equivalence
```

### R2 - Must Defeat Factorized / Per-Component Lookup

Required revision: require the future memory-resistance mechanism to defeat
exact-key lookup, factorized lookup, per-component nearest-neighbor lookup,
partial-key lookup, topology-only lookup, risk-only lookup, signal-action
lookup, and action-conditioned nearest-neighbor lookup.

Required blocker:

```text
blocked_by_factorized_lookup_equivalence
```

### R3 - Leakage Positive-Control Panel

Required revision: replace one positive control with a predeclared leakage
positive-control panel covering observation-name leakage, action-name leakage,
filename leakage, fixture-name leakage, candidate-authored alias leakage,
future-observation leakage, hidden truth label leakage, and answer-encoding
metadata leakage.

Required blockers:

```text
blocked_by_non_fail_able_leakage_scanner
blocked_by_whitelist_leakage_scanner
```

### R4 - Multi-Seed Stability For Mechanism-Relevant Effect Candidate

Required revision: require any `mechanism_relevant_effect_candidate`
classification to reproduce across predeclared seeds, with per-seed candidate
score, strongest-baseline score, delta, mean delta, dispersion or confidence
interval, and a noise failure rule.

Required blocker or downgrade:

```text
inconclusive
blocked_by_unstable_or_noise_level_effect
```

The B3 bands remain:

- equivalence: `< 0.02`
- inconclusive: `[0.02, 0.05)`
- mechanism-relevant effect candidate: `>= 0.05`

Crossing `>= 0.05` on one seed does not by itself justify
`mechanism_relevant_effect_candidate`.

### R5 - Anti-Zeno Detector-Bound Closure

Required revision: bind collapse to operational detector outputs and require
closure or downgrade if 001B triggers any collapse condition.

Collapse conditions:

- `baseline_equivalent`
- `blocked_by_baseline_equivalence`
- `blocked_by_factorized_lookup_equivalence`
- `blocked_by_candidate_truth_coupling`
- `oracle_like_reference_candidate_scaffolding_only` used as evidence
- `blocked_by_non_discriminative_distribution`
- `blocked_by_solvability_preflight_failure`
- `blocked_by_unsolvable_or_leaky_distribution`

Required route:

```text
close_or_downgrade_current_acp_bv_surface_family
```

Required closure artifact:

```text
artifacts/acp_bv_001b_collapse_closure_*/result.json
```

## Nonblocking R6

Claude suggested these defense-in-depth additions as recommended but
nonblocking:

1. candidate-vs-truth behavioral equivalence probe on heldout probe cases;
2. predeclared strongest-baseline selector as `argmax(score)` over executed
   fair baselines;
3. namespace clarification distinguishing prior ACP-BV surface-spec 001B from
   distribution-redesign spec 001B.

R6 is not a blocker for this revision task, but it must not weaken R1-R5.

## Claim Ceiling And Forbidden Claims

Maximum claim:

```text
001b_redesign_spec_r1_r5_ready_for_independent_reaudit
```

This preservation record and the revised spec do not claim ACP-BV validity,
ACP-BV mechanism validity, harness validity, Gate validity, admission
readiness, bridge readiness, runtime readiness, mainline effect, agency
evidence, consciousness, real emotion, autonomy, stable user benefit, or EGO
readiness.

## What This Does Not Prove

This does not prove that ACP-BV is valid, that ACP-BV 001B is implementable, or
that the future distribution will defeat fair baselines. It only preserves
Claude's hostile spec audit and records the bounded R1-R5 revisions needed
before a targeted independent re-audit.
