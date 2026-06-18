# DRAFT-ROUTE-C-CANDIDATE-CARD-001A-R1

Artifact copy of the revised Route C candidate-card contract.

Date drafted: 2026-06-16

## Status

- Card status: R1 candidate-card revision only.
- Implementation authorized: false.
- Candidate implementation authorized: false.
- Gate/mainline/runtime/live integration authorized: false.
- Push/tag/remote-anchor authorized: false.
- Auto-Remote-Anchor: forbidden.

This artifact is not an implementation card. It preserves the R1 contract that a
future, separately authorized implementation card would have to satisfy before
Route C candidate code can be written.

## Problem Definition

The prior draft candidate-card was independently audited and received:

`requires_candidate_card_revision_before_implementation_authorization`

R1 revises the candidate-card contract to close B1-B5 without creating candidate
implementation, Gate integration, mainline wiring, runtime path, push, tag, or
remote anchor.

## Layer / Status Fields

- Current layer: `engineering-governance / candidate-card audit preservation + card revision only`.
- Mainline integration status: none.
- Enabled status: none.
- Real trigger evidence: local file preservation and documentation artifact only.
- Claim ceiling: candidate-card audit preservation and revised candidate-card contract only.

## Prior Negative Evidence Cited

- ACSB downgrade closure:
  `docs/research/ACSB-CURRENT-ROUTE-DOWNGRADE-CLOSURE-001A.md`.
- ACOLB-A saturation closure:
  `docs/research/CLAUDE-INDEPENDENT-ACOLB-A-ROUTE-DECISION-AND-ROUTE-C-DESIGN-AUDIT-001A.md`
  and `docs/decision_log.md`.
- Route C Phase 0 repaired preflight re-audit:
  `docs/research/CLAUDE-INDEPENDENT-ROUTE-C-PREFLIGHT-001A-REPAIR-REAUDIT-001A.md`.

## B1. Provenance F-Forge Closure

Every future candidate-run material row must be validated by re-executing the
recorded producer function on recorded inputs and asserting output equality with
the recorded value, or by rederiving the recorded basis from recorded inputs.

Self-declared basis consistency is insufficient.

Required positive control: a self-consistent forged value/basis pointing to a
true producer must be injected and blocked. This applies to candidate-run
evidence, not only future Gate-level reuse.

## B2. Passive Baseline Family Superset

The passive family must be a superset of the accepted Phase 0 passive family.
No accepted Phase 0 passive attacker may be removed or weakened.

Required included attackers:

- `legal_field_membership_attacker`
- `passive_mean_attacker`
- `passive_variance_attacker`
- `passive_correlation_attacker`
- `passive_pca_subspace_attacker`
- `passive_cross_episode_attacker`
- `supervised_passive_feature_attacker`
- `positional_first_k_attacker` or equivalent positional attacker

`obs_only_family_max` must be max over the union of accepted Phase 0 attackers
and any new attackers.

## B3. Fair-Interventional Baseline Hardening

The mechanism component under test must be predeclared, minimal, and
independently specified. The strongest fair baseline must have access parity
with the candidate except for that one minimal component.

Required artifact:

- `access_parity_report.json`

It must compare intervention budget, API, observations, action space, state
access, update access, train/heldout access, counterfactual-pair access, seed
access, replay inputs, and evaluator-only field exclusion.

Required positive control: when the tested mechanism component is granted to the
strongest fair baseline, that baseline must approach candidate performance
within the frozen equivalence band. Otherwise the baseline is unfair or
impoverished and the run is invalid.

No vague exception may weaken the fair baseline.

## B4. Demonstrated Fail-Able Margin And Saturation Gates

The margin gate must include a demonstrated failing negative control where a
synthetic candidate fails the frozen margin and the gate returns
`close_or_downgrade`.

The saturation gate must include a demonstrated failing negative control where a
fair interventional baseline saturates the candidate and the gate returns
`close_or_downgrade`.

Every material gate must ship a demonstrated failing negative control.

## B5. Graph-Cache Family

The fair-interventional saturation panel must include all six graph-cache
challengers:

- `graph_lookup`
- `transition_table`
- `successor_map`
- `count_table`
- `fsm_planner`
- `episodic_traversal`

All six must be callable, provenance-recorded, and included in the saturation
judgment.

## Non-Blocking Improvements Incorporated

- N1: governing ACSB downgrade and ACOLB-A saturation negatives are cited.
- N2: future implementation-card stage must predeclare and hash all margin
  values before run.
- N3: replay section must state tautological controls do not count toward
  failability.
- N4: truth self-set seed must be disjoint from candidate and baseline
  observation seeds.

## Future Implementation-Card Requirements

A future card must require:

- `stage0_margin_freeze_manifest.json`
- `stage0_margin_freeze_manifest.sha256`
- `margin_gate_report.json`
- `margin_gate_negative_control_report.json`
- `saturation_gate_report.json`
- `saturation_gate_negative_control_report.json`
- `access_parity_report.json`
- `feature_impoverishment_control_report.json`
- `provenance_forge_positive_control_report.json`
- `seed_isolation_report.json`
- replay recomputation from serialized state plus legal observations and
  interventions
- no unused frozen seed, train context, heldout context, or counterfactual pair

Tautological replay controls do not count toward failability. Load-bearing
replay controls must mutate serialized state or legal intervention rows and
demonstrate changed recomputed behavior or a fail-closed verdict.

## Acceptance Gate

This R1 artifact is acceptable only as a revision artifact if:

- preserved audit evidence exists locally;
- B1-B5 are explicitly closed;
- N1-N4 are incorporated;
- implementation remains forbidden;
- Gate/mainline/runtime/source/test/script paths remain untouched;
- Auto-Remote-Anchor remains forbidden;
- claim ceiling remains candidate-card revision only.

## Stop Condition

Stop if any source, test, script, Gate runner, mainline, runtime, scheduler,
bridge, product/admission, credential, push, or deployment file is modified; if
candidate implementation is introduced; if push/tag/remote-anchor is attempted;
if a secret is printed, copied, exposed, or modified; or if any claim says Route
C works, candidate is authorized, Gate passed, mainline effect exists, or
mechanism evidence has been produced.

## Claim Ceiling

Candidate-card audit preservation and revised candidate-card contract only. No
mechanism evidence, no candidate evidence, no Gate pass, no mainline effect, no
live path, no agency, no autonomy, no consciousness, no emotion, no stable user
benefit, no EGO readiness, and no claim that Route C works.

## Next Minimal Closed-Loop Action

Independent hostile audit of R1. Candidate implementation remains forbidden
unless that future audit accepts the card and a separate bounded implementation
task card explicitly authorizes implementation scope.

