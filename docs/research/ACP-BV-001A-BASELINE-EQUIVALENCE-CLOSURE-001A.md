# ACP-BV 001A Baseline Equivalence Closure 001A

Task id: `ACP-BV-001A-BASELINE-EQUIVALENCE-CLOSURE-001A`

Closure verdict: `blocked_by_baseline_equivalence`

## Layer And Status

Current layer: mechanism-hypothesis / engineering-governance route closure only.

Mainline integration status: none.

Enabled status: none. This document creates no Gate, bridge, runtime,
admission, scheduler, live path, mainline path, or real Gate target.

Real trigger evidence:

- Final anchored HEAD:
  `c105a965de9e05dfdea7bc77b393bd5c85e43754`
- Local and remote tag:
  `remote-anchor-acp-bv-harness-001a-fair-baseline-equivalence-repair-001a-c105a96`
- Preserved verdict: `blocked_by_baseline_equivalence`
- Claim ceiling:
  `current_001a_distribution_exposes_baseline_equivalence_or_non_discriminative_surface`

Claim ceiling for this closure:
ACP-BV 001A negative-evidence closure and ACP-BV 001B distribution redesign
spec only.

Next minimal closed-loop action: send
`docs/research/ACP-BV-DISTRIBUTION-REDESIGN-SPEC-001B.md` for independent
hostile spec audit before any ACP-BV 001B implementation task is drafted.

## Closed Result

ACP-BV harness 001A is closed as non-discriminative under the current
distribution.

001A must not be repaired further into a pass-shaped result. The decisive
blocker is a fair full-access lookup baseline that tied the reference candidate:

| Field | Value |
| --- | --- |
| strongest baseline | `full_access_lookup_baseline` |
| candidate score | `1.0` |
| baseline score | `1.0` |
| delta | `0.0` |
| B3 classification | `baseline_equivalent` |
| train/heldout overlap | `18/18` |
| overlap ratio | `1.0` |
| memory lookup complete policy | `true` |
| candidate/truth coupling | `oracle_like_reference_candidate_scaffolding_only` |

The current distribution allows a fair memory or lookup baseline to be a
complete policy. That means the surface does not distinguish the intended
ACP-BV mechanism hypothesis from memorization over the visible train/heldout
key structure.

## Candidate And Truth Coupling

The preserved 001A artifact classifies the reference candidate as
`oracle_like_reference_candidate_scaffolding_only`.

The reference candidate must not be cited as mechanism-relevant evidence,
because the candidate path and truth-generator path are formula-coupled under
the current scaffold. This coupling is evidence about the weakness of the
001A surface, not evidence that ACP-BV works.

## Required Preservation

The following interpretations are preserved as closure requirements:

1. ACP-BV 001A is negative evidence for the current distribution.
2. `baseline_equivalent` is a blocker, not pass.
3. Full-access lookup was the strongest fair baseline and must not be replaced
   by a weaker graph-cache challenger in the closure narrative.
4. Candidate/truth formula coupling makes 001A scaffolding only.
5. The source-pin repair proves fail-able git-object source-boundary behavior
   only; it does not repair the distribution into a discriminative benchmark.
6. The tamper negative control blocked with
   `blocked_by_unpinned_boundary_verifier`, which preserves source-boundary
   evidence but does not defeat lookup equivalence.

## Future 001B Inheritance

Any future ACP-BV 001B must inherit these hard constraints:

- true heldout generalization with heldout keys, configurations, or latent
  combinations not present in training;
- fair full-access lookup baseline included from the start;
- strongest-baseline selection after execution;
- B3 bands preserved with `< 0.02` equivalence, `[0.02, 0.05)`
  inconclusive, and `>= 0.05` mechanism-relevant-effect candidate;
- no candidate/truth formula coupling;
- independent solvability preflight;
- no candidate-authored truth, difficulty, threshold, generator selection,
  baseline construction, or verdict influence;
- repaired source-boundary and git-object frozen source-pin requirements
  carried forward;
- one redesign attempt before closure or downgrade if the family collapses
  again.

## What This Does Not Prove

This closure does not disprove ACP-BV as a broader mechanism hypothesis. It
only records that ACP-BV 001A, under the current distribution, is
non-discriminative because a fair full-access lookup baseline ties the
candidate and the reference candidate is scaffold-coupled to the truth path.

This closure does not prove ACP-BV validity, ACP-BV mechanism validity, harness
validity, Gate validity, admission readiness, bridge readiness, runtime
readiness, mainline effect, agency evidence, consciousness, real emotion,
autonomy, stable user benefit, or EGO readiness.
