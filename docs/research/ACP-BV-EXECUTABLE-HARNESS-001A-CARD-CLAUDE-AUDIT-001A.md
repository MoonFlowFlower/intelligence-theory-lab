# ACP-BV Executable Harness 001A Card Claude Audit 001A

Task id: `ACP-BV-EXECUTABLE-HARNESS-001A-CARD-R1-REVISION-001A`

Status: preserved independent card-level audit requiring task-card revision
before any harness implementation.

Current layer: engineering-governance / task-card audit preservation only.

Mainline integration status: none.

Enabled status: none.

Real trigger evidence:

- Starting commit reported by the current task:
  `42b94d06b9cddb9e5679468d1a21f66d3f7d1022`.
- Starting tag reported by the current task:
  `remote-anchor-acp-bv-001b-reaudit-harness-card-draft-001a-42b94d0`.
- Prior verdict reported by the current task:
  `acp_bv_harness_card_draft_ready_for_independent_review`.
- Independent card-level audit verdict preserved here:
  `requires_card_revision_before_implementation`.

## Preserved Verdict

Claude's independent card-level audit verdict:

`requires_card_revision_before_implementation`

The audit found 11 of 12 hostile checks acceptable, but blocked implementation
authorization on B4/B5 because `repo-source-owned` and
`candidate-inaccessible` could still be treated as self-declared fields rather
than derived, fail-able, repo-owned verification outputs.

## Blocking Issue R1

Required revision R1:

- Add a hard binding requiring the future harness implementation to include a
  repo-owned callable verifier that derives source ownership and
  candidate-inaccessibility for every load-bearing callable.
- The verifier must derive these properties from actual resolved source paths
  and explicit path-boundary rules.
- The future harness must not accept self-declared fields such as
  `repo_source_owned: true`, `candidate_inaccessible: true`,
  `trusted_source: true`, `source_owned_by_harness: true`, or any equivalent
  static or candidate-authored declaration.
- At least one fail-able negative control must prove that a
  candidate-accessible generator or truth source is automatically rejected.
- The future card must add a stop condition for ownership or inaccessibility
  accepted from declaration rather than derived by the verifier.

Preserved blocker wording:

`repo-source-owned / candidate-inaccessible self-declaration gap`

Preserved route consequence:

No ACP-BV harness implementation is authorized until the R1 task-card revision
is completed and independently re-audited with an accept verdict.

## B1-B5 Audit Readback

| Binding | Preserved audit result | Preservation note |
| --- | --- | --- |
| B1 counterfactual action and difficulty control | PASS | Harness-selected counterfactual action probes and forbidden candidate difficulty sources were present. |
| B2 real control execution, no self-reported booleans | PASS | Callable execution artifacts and clean/dirty controls were required; self-reported pass flags were not load-bearing. |
| B3 baseline equivalence band | PASS | `<0.02`, `[0.02, 0.05)`, and `>=0.05` bands were present, with baseline equivalence not pass. |
| B4 source-hash provenance | PARTIAL / blocking | Source identity/hash was required, but repo ownership could still be recorded as a declaration rather than derived. |
| B5 candidate-inaccessible generators | PARTIAL / blocking | Candidate-inaccessibility was required, but no fail-able control proved a candidate-accessible generator would be rejected. |

## Hostile-Check Summary

The preserved audit classified the following as blocked or acceptable:

- fake-pass route: blocked except for the R1 self-declared ownership residue.
- circular truth route: B5 blocked the property, with the same R1 residue.
- candidate-authored ground truth: B5 forbidden, with the same R1 residue.
- candidate-selected difficulty: blocked by B1.
- weak baseline matrix: not found; graph-cache family and related baselines
  were required.
- non-fail-able scanner: clean/dirty controls made it fail-able, with N1 as a
  non-blocking hardening suggestion.
- hash-only replay: blocked.
- field-deletion ablation: mostly blocked, with N2 as a non-blocking hardening
  suggestion.
- provenance present-but-not-load-bearing: blocking R1 issue.
- claim inflation: not found.
- scope creep: not found.
- missing stop condition: missing ownership/inaccessibility self-declaration
  stop condition, folded into R1.

## Non-Blocking Suggestions Preserved

N1 leakage dirty-control randomization:

- Dirty-control injection should be repo-owned and vary across seeds or cases
  in alias/name, nested location, and value encoding or representation.
- This prevents a structurally blind scanner from passing by recognizing only a
  fixed injected field name.

N2 ablation must rerun episodes:

- Ablation must not be implemented as deleting, masking, or editing report
  fields.
- Ablation must rerun episodes under real input/component intervention and
  regenerate the full trace.
- The future harness must persist intervention target, rerun command, run ID,
  regenerated trace path, before/after metrics, effect size, and threshold
  classification.

N3 threshold band change rule:

- The `<0.02`, `[0.02, 0.05)`, and `>=0.05` baseline-effect bands are immutable
  by default.
- Any future change to these bands must be generated before candidate scoring
  by repo-owned code from a recorded baseline-error distribution.
- The change record must include producer function, source hash, seed,
  baseline distribution input, generated thresholds, and artifact path.
- Post-hoc threshold changes after seeing candidate score are forbidden.

## Claim Ceiling

This preservation document supports only:

`ACP-BV harness task-card R1 revision and Claude card-audit preservation`

This does not claim:

- ACP-BV validity;
- harness readiness;
- harness validity;
- Gate validity;
- mechanism validity;
- admission readiness;
- bridge readiness;
- runtime readiness;
- mainline effect;
- agency evidence;
- consciousness;
- real emotion;
- autonomy;
- stable user benefit;
- EGO readiness.

## What This Does Not Prove

This document preserves a card-level audit and its blocker. It does not execute
the ACP-BV harness, does not run baseline, ablation, replay, leakage, or Gate
experiments, and does not prove the R1 revision is sufficient until targeted
independent re-audit accepts the revised task card.
