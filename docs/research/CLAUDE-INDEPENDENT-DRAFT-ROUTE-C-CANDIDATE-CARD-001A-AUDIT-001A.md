# CLAUDE-INDEPENDENT-DRAFT-ROUTE-C-CANDIDATE-CARD-001A-AUDIT-001A

Read-only audit preservation for `DRAFT-ROUTE-C-CANDIDATE-CARD-001A`.

Date preserved: 2026-06-16

## Preservation Status

- Audit source: operator-provided Claude read-only audit summary in the current Codex task attachment.
- Preservation mode: faithful local preservation of audit verdict, blockers, and required R1 revisions.
- Codex role in this file: preservation only.
- Codex did not perform an independent re-audit.
- Implementation authorization: false.
- Gate/mainline/runtime authorization: false.
- Push/tag/remote-anchor authorization: false.

## Verdict Preserved

`requires_candidate_card_revision_before_implementation_authorization`

The audited draft was not accepted for implementation. Route C candidate
implementation remains forbidden until a revised candidate-card is independently
audited and separately authorized.

## Current Layer

`engineering-governance / candidate-card audit preservation only`

## Mainline Integration Status

None. This audit preservation does not touch or authorize any Gate, mainline,
runtime, bridge, scheduler, admission, product, deployment, UI, LLM, AIRI, or
EGO-mainline path.

## Enabled Status

None. No CLI candidate, pytest candidate, Gate runner, runtime path, or live
Route C path is enabled by this preservation.

## Real Trigger Evidence

Local file preservation of the operator-provided Claude read-only audit summary
and its required revision set only.

## Blocking Required Revisions

### B1. Provenance F-forge Closure

Candidate-run material rows must be validated by re-executing producer
functions on recorded inputs and asserting output equality with the recorded
value, or by rederiving the recorded basis from recorded inputs.

The revised card must require a forged-provenance positive control: inject a
self-consistent forged value/basis pointing to a true producer; the provenance
gate must block.

This applies to candidate-run evidence, not only future Gate-level reuse.

### B2. Passive Baseline Family Superset

The revised card must require the passive family to be a superset of the
accepted Phase 0 passive family.

It must explicitly include mean, variance, correlation, PCA-subspace,
cross-episode, supervised passive feature attacker, and positional attacker.

`obs_only_family_max` must be the maximum over the union of the accepted Phase 0
family plus any new attackers.

### B3. Fair-Interventional Baseline Hardening

The mechanism component under test must be predeclared, minimal, and
independently specified.

The revised card must require an access-parity artifact comparing candidate and
strongest fair baseline intervention budget, API, observations, action space,
state access, and update access.

It must require a feature-impoverishment positive control: when the tested
mechanism component is granted to the fair baseline, that baseline must approach
candidate performance. Otherwise the baseline is considered unfair or
impoverished and the run is invalid.

Any vague exception that can weaken the fair baseline must be removed.

### B4. Demonstrated Fail-Able Margin And Saturation Gates

The margin gate must include a demonstrated failing negative control where a
synthetic candidate fails the frozen margin and the gate returns
`close_or_downgrade`.

The saturation gate must include a demonstrated failing negative control where a
fair interventional baseline saturates the candidate and the gate returns
`close_or_downgrade`.

Every material gate must ship a demonstrated failing negative control.

### B5. Graph-Cache Family

The interventional graph-cache challenger family must enumerate all six required
challengers:

- `graph_lookup`
- `transition_table`
- `successor_map`
- `count_table`
- `fsm_planner`
- `episodic_traversal`

All six must be included in the saturation judgment.

## Non-Blocking Improvements Required For R1

- N1: cite governing prior negatives in the card text: ACSB downgrade closure
  and ACOLB-A saturation closure.
- N2: require any implementation-card stage to predeclare and hash margin values
  before run.
- N3: replay section must state tautological controls do not count toward
  failability.
- N4: add truth-seed isolation: ground-truth self-set seed must be disjoint from
  any candidate or baseline observation seed.

## Claim Ceiling

Candidate-card audit preservation only. This file does not prove Route C
mechanism validity, candidate evidence, Gate pass, mainline effect, live path,
agency, autonomy, consciousness, emotion, stable user benefit, or EGO readiness.

## Next Minimal Closed-Loop Action

Draft and independently audit `DRAFT-ROUTE-C-CANDIDATE-CARD-001A-R1`. Candidate
implementation remains forbidden until that future audit separately authorizes a
bounded implementation card.
