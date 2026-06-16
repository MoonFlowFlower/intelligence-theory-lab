# ACP-BV 001B Implementation Task Card 001A Claude Audit 001A

Task id: `ACP-BV-001B-IMPLEMENTATION-TASK-CARD-001A-CLAUDE-AUDIT-001A`

Preserved verdict:

```text
requires_implementation_card_revision_before_implementation
```

## Current Layer

`mechanism-hypothesis / engineering-governance implementation-task-card revision only`

## Mainline Integration Status

No EGO mainline integration. No Gate, bridge, admission, runtime, scheduler,
live, deployment, companion, AIRI, LLM, or UI path is authorized or touched by
this preservation record.

## Enabled Status

Not enabled. This is a documentation and artifact preservation task only.

## Real Trigger Evidence Inspected

- Audited card:
  `docs/research/ACP-BV-001B-IMPLEMENTATION-TASK-CARD-001A.md`
- Audited commit:
  `7715dfd1322e416dc150fbbd7dde005d669180fb`
- Audited tag:
  `remote-anchor-acp-bv-001b-implementation-task-card-001a-7715dfd`
- Audit verdict:
  `requires_implementation_card_revision_before_implementation`
- Current revision task start readback:
  local HEAD, local tag, remote branch, and remote tag resolved to
  `7715dfd1322e416dc150fbbd7dde005d669180fb`.

## Files Inspected

- `docs/research/ACP-BV-001B-IMPLEMENTATION-TASK-CARD-001A.md`
- `docs/research/ACP-BV-DISTRIBUTION-REDESIGN-SPEC-001B.md`, read-only
- `artifacts/acp_bv_001b_implementation_task_card_001a/result.json`
- `artifacts/acp_bv_001b_implementation_task_card_001a/validation.json`

## Implementation-Card Scope Result

Scope was clean at the audited boundary. The audited card was a future
implementation task card only, not ACP-BV 001B execution authorization. The
audit did not reopen the R1-R5 spec revision and did not authorize source,
test, Gate, bridge, admission, runtime, scheduler, live, or mainline work.

## Binding #1 Audit Result

Binding #1 was present but insufficiently fail-able.

The audited card required paired detector controls and required recording
expected-vs-actual flip results. It did not explicitly require the future
implementation to assert the predeclared flip and block when:

```text
actual_flip != predeclared_expected_flip
```

This allowed a detector-stub or non-fail-able detector to be recorded as a
caveat while the future implementation continued.

Required revision: upgrade detector fail-ability to record + assert +
block-on-divergence for every operational detector.

## Binding #2 Audit Result

Binding #2 was present but insufficient against whitelist scanners.

The audited card required renamed or structural variants for leakage positive
controls. One predeclared variant per leakage class could still be defeated by
whitelisting the original fixture plus that known variant.

Required revision: require at least two structural variants per leakage class,
with at least one runtime-generated or held-out variant per class, plus scanner
source string-literal disjointness audit before accepting scanner detection.

## Binding #3 Audit Result

Binding #3 was present as a per-seed episode-floor requirement, but the audit
requested nonblocking hardening to make the floor concrete in this card.

Required hardening incorporated by the revision: at least
`128 heldout evaluation episodes per seed` across seeds
`[1009, 2027, 3037, 4049, 5051]`, with
`blocked_by_insufficient_distribution_capacity`,
`blocked_by_unstable_or_noise_level_effect`, or `inconclusive` outcomes if the
floor cannot be met under the predeclared constraints.

## Binding #4 Audit Result

Binding #4 was present as factorization-family completeness. The revision
keeps this binding and carries it into terminal collapse classification when a
lookup-complete axis or factorized lookup equivalence is discovered.

## Computed-Evidence Gate Result

The computed-evidence gate was present, including callable computation paths
for scores, baselines, ablations, leakage scans, replay, and source-boundary
checks. The audit required strengthening the gate so detector controls cannot
be warning-only and leakage scanner claims cannot rely on method statements
without runtime/held-out positive controls and string-literal disjointness
evidence.

## Baseline Matrix Result

The baseline matrix was strong. It included lookup, factorized, per-component,
partial-key, topology, risk, signal-action, nearest-neighbor, graph-cache,
transition-table, successor-map, count-table, episodic-traversal, FSM planner,
and query-capable imitation families where applicable. The audit did not
require weakening or replacing the baseline matrix.

## Source-Boundary / Source-Pin Result

Source-boundary and source-pin contracts were present. The audited card carried
forward the 001A repaired standard: git-object frozen anchor, callable
source-boundary verification, tamper-after-anchor negative control, rejection
of self-declared repo-source fields, and rejection of unpinned or stale
worktree claims.

## Anti-Zeno Result

Anti-Zeno closure existed in principle, but the card did not explicitly
separate terminal distribution/surface collapse from repairable
harness-integrity failures.

Required revision: classify future failure verdicts into:

- terminal distribution/surface collapse, forcing
  `close_or_downgrade_current_acp_bv_surface_family` and forbidding 001C/001D
  repair attempts;
- repairable harness-integrity failure, repairable only inside the already
  authorized 001B implementation-card scope and not citable as mechanism,
  harness, Gate, or surface evidence while unresolved.

## Strongest Remaining Objection

Without the required revision, ACP-BV 001B could still false-pass through:

- a detector path that records a failed paired control but does not block; or
- a leakage scanner that recognizes only the original fixture and one known
  renamed variant per class.

Both paths would preserve the historical false-pass risk rather than producing
discriminative mechanism evidence.

## Required Revisions

1. Add Binding #1 divergence-must-block clause:
   `actual_flip != predeclared_expected_flip` must force
   `blocked_by_non_fail_able_detector`.
2. Upgrade Binding #2 anti-whitelist leakage controls: at least two structural
   variants per leakage class, with one runtime-generated or held-out variant,
   scanner source string-literal disjointness audit, and
   `blocked_by_whitelist_leakage_scanner` on failure.
3. Add Anti-Zeno classification closure for terminal distribution/surface
   collapse versus repairable harness-integrity failure.
4. Incorporate hardening directly into the card: concrete per-seed episode
   floor, novelty-floor values, five-seed multi-seed stability rule, shared
   helper candidate/truth decoupling analysis, leaking-oracle invalidity, and
   closure artifact path/fields.

## Claim Ceiling

ACP-BV 001B implementation-task-card revision and hostile-audit preservation
only.

This does not prove ACP-BV validity, mechanism validity, harness validity, Gate
validity, admission readiness, bridge readiness, runtime readiness, mainline
effect, agency, consciousness, emotion, autonomy, stable user benefit, or EGO
readiness.

## Next Minimal Closed-Loop Action

Send the revised
`docs/research/ACP-BV-001B-IMPLEMENTATION-TASK-CARD-001A.md` to Claude for
targeted independent hostile re-audit of the card revision.

Do not implement ACP-BV 001B until the revised implementation task card is
independently accepted.
