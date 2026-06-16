# ACP-BV Distribution Redesign Spec 001B Claude Reaudit 001A

Task id: `ACP-BV-DISTRIBUTION-REDESIGN-SPEC-001B-CLAUDE-REAUDIT-001A`

Preservation status: Claude R1-R5 targeted reaudit preserved for future
implementation task-card drafting only.

## Verdict

```text
accept_for_001b_implementation_task_card_drafting
```

This verdict accepts the revised ACP-BV 001B distribution-redesign spec only as
adequate input for a future implementation task card. It does not authorize ACP-
BV 001B implementation, source changes, tests, Gate execution, bridge,
admission, runtime, scheduler, mainline, or real Gate target work.

## Layer And Status

Current layer: mechanism-hypothesis / engineering-governance implementation-
task-card drafting only.

Mainline integration status: none.

Enabled status: none. This preservation record creates no Gate, bridge,
runtime, admission path, scheduler, live path, mainline path, real Gate target,
candidate, harness, or enabled execution path.

Real trigger evidence inspected:

- start commit:
  `cf757ad30dd151ae77e27102679489df2653ca25`
- start tag:
  `remote-anchor-acp-bv-001b-redesign-spec-r1-r5-revision-001a-cf757ad`
- revised redesign spec:
  `docs/research/ACP-BV-DISTRIBUTION-REDESIGN-SPEC-001B.md`
- prior Claude audit preservation:
  `docs/research/ACP-BV-DISTRIBUTION-REDESIGN-SPEC-001B-CLAUDE-AUDIT-001A.md`
- revision artifacts:
  `artifacts/acp_bv_001b_redesign_spec_r1_r5_revision_001a/result.json`
  and
  `artifacts/acp_bv_001b_redesign_spec_r1_r5_revision_001a/revision_matrix.json`

Files inspected:

- `docs/research/ACP-BV-DISTRIBUTION-REDESIGN-SPEC-001B.md`
- `docs/research/ACP-BV-DISTRIBUTION-REDESIGN-SPEC-001B-CLAUDE-AUDIT-001A.md`
- `artifacts/acp_bv_001b_redesign_spec_r1_r5_revision_001a/result.json`
- `artifacts/acp_bv_001b_redesign_spec_r1_r5_revision_001a/readback.json`
- `artifacts/acp_bv_001b_redesign_spec_r1_r5_revision_001a/claude_spec_audit_preservation.json`
- `artifacts/acp_bv_001b_redesign_spec_r1_r5_revision_001a/revision_matrix.json`

## Preserved Claude Reaudit Result

Claude accepted that the revised 001B redesign spec closes the predeclared
R1-R5 gaps at the spec layer:

- R1: baseline-equivalence blocking now applies beyond exact overlap, and the
  heldout novelty floor is predeclared with persisted novelty/B3 readbacks.
- R2: the spec now requires resistance to exact-key, factorized,
  per-component, partial-key, topology-only, risk-only, signal-action, and
  action-conditioned nearest-neighbor lookup.
- R3: the leakage positive-control panel now covers eight leakage classes and
  includes fail-able scanner blockers.
- R4: any `mechanism_relevant_effect_candidate` classification now requires
  multi-seed stability, per-seed score/delta readback, dispersion reporting, and
  sampling-noise downgrade/block rules.
- R5: Anti-Zeno closure is now detector-bound, with 001B collapse requiring
  `close_or_downgrade_current_acp_bv_surface_family` rather than 001C/001D
  repair into a pass-shaped result.

R6 handling: R6 remains recommended defense-in-depth, not a blocker for the
redesign spec itself. Future implementation-card deferral of any R6 item must
be explicit and must not weaken R1-R5.

Regression result: no regression was identified at the spec layer. The revised
spec remains implementation-unauthorizing, keeps B3 equivalence and
inconclusive bands, keeps candidate/truth decoupling, preserves no candidate-
authored truth, and carries forward source-boundary/source-pin requirements from
001A.

## Strongest Remaining Objection

The strongest remaining objection is implementation-card-level, not spec-layer:
detector fail-ability is uneven. If the future implementation card merely names
detectors without requiring paired fail-able controls, 001B could still collapse
into non-fail-able or stub-fed detector success.

The future implementation card must therefore make detector fail-ability a hard
acceptance gate, not an optional audit note.

## Implementation-Card-Level Required Bindings

The future ACP-BV 001B implementation task card must bind at least:

1. Unified detector fail-ability: every operational detector must have a
   predeclared paired negative control that injects an intervention expected to
   flip the corresponding verdict, and the future implementation must run and
   record expected-vs-actual flips. Missing paired control must force
   `blocked_by_non_fail_able_detector`.
2. Leakage positive controls are structural, not name-whitelist checks: the
   leakage scanner must detect the eight positive-control classes by structure,
   with renamed or structurally varied probes. Catching only original fixture
   names must force `blocked_by_whitelist_leakage_scanner`.
3. Per-seed episode floor: the future card must set a minimum per-seed episode
   count or explicitly justify the floor. Too-small budgets for B3,
   dispersion, or CI decisions must downgrade to `inconclusive` or block as
   `blocked_by_unstable_or_noise_level_effect`.
4. Factorization family completeness: the future card must predeclare all
   factorization families used by novelty and lookup-equivalence detectors and
   explain why no undeclared axis creates a lookup-complete channel. A
   post-execution undeclared lookup-complete axis must force
   `blocked_by_factorized_lookup_equivalence`.

## Claim Ceiling

Maximum claim:

```text
ACP-BV 001B implementation-task-card drafting and R1-R5 reaudit preservation only
```

This does not prove ACP-BV validity, mechanism validity, harness validity, Gate
validity, admission readiness, bridge readiness, runtime readiness, mainline
effect, agency, consciousness, emotion, autonomy, stable user benefit, or EGO
readiness.

## Next Minimal Closed-Loop Action

Send `docs/research/ACP-BV-001B-IMPLEMENTATION-TASK-CARD-001A.md` to Claude for
independent hostile audit of the implementation task card.

Do not implement ACP-BV 001B until the implementation task card itself is
independently accepted.
