# Hostile Audit — GATE1-REPLACEMENT-PREFLIGHT-00XA Implementation-Card Draft

Audit ID: `CLAUDE-INDEPENDENT-GATE1-REPLACEMENT-PREFLIGHT-00XA-IMPLEMENTATION-CARD-HOSTILE-AUDIT-001A`
Date: 2026-06-17
Role: same-agent-bridge-audit-role-001 / independent red-team (implementation-card level)
Predecessor: R1 re-audit (`r1_accepted_for_implementation_card_drafting`)

## Verdict

**`implementation_card_accepted_surface_spec_required_before_implementation`**

- implementation may proceed now: **false**
- pre-existing independently frozen surface spec required before implementation: **true (hard precondition)**
- implementation-card drafter allowed to create or mutate that spec: **false** (and it did not)
- remaining blocking issue: **none**

## Claim ceiling

Implementation-card draft acceptance only. Not Gate1 admissibility, not a Gate run, not a
candidate task, not runtime/mainline/admission/bridge wiring, not an admission result. No Gate
evidence produced. The maximum downstream verdict (`admissible_for_candidate_card_drafting_only`)
authorizes at most candidate-card drafting.

## What was checked and how

All target files were read via the authoritative file API (not bash), to avoid the known FUSE
mount-tail truncation trap. No truncation was observed: the implementation card closes cleanly at
line 602 (§33), the R1-accepted source card at line 527, and the cited R1 `audit_result.json` at
line 78.

Three independent cross-checks drive the verdict:

1. **The R1 authorization is real, not self-declared.** The cited
   `audit_result.json` carries `verdict=r1_accepted_for_implementation_card_drafting`,
   `implementation_may_proceed_now=false`, `remaining_blocking_issue=none`. This matches the
   auditor's own independent prior R1 re-audit record and matches `r1_reaudit_readback.json`
   field-for-field. The audit_result SHA (`62217c5a…`) is identical across `source_readback.json`
   and `r1_reaudit_readback.json`. (Exact byte-hash recompute through the mount is unreliable;
   verification is by file-API content corroboration, not independent hashing.)

2. **The port preserved or strengthened every R1-accepted constraint.** A line-by-line diff of the
   527-line R1-accepted card against the 602-line implementation card found **no weakening**.
   R1.a (balanced metric, six single-sided bans, degenerate controls, size-only sweep,
   no-by-reference-escape), R1.b (positive fail-able partial-inferability + budget-faithful oracle),
   and R1.c (surface-spec immutability) are all carried forward. Several sections are strengthened:
   the forbidden-files list now explicitly bans any surface-spec creation/mutation/freeze; the
   acceptance gate adds the oracle equivalence-band clearance; and the stop condition adds an
   explicit post-hoc metric/band stop — which closes the one non-blocking note from the R1
   re-audit.

3. **The drafter did not author a surface spec.** The card specifies the spec's required *contents*
   as acceptance criteria but supplies no values, schema, metric, or equivalence band.
   `source_mutation_performed=false` and no spec file appears in the generated set.

## 15 critical checks

| # | Check | Result |
|---|-------|--------|
| 1 | Preserves R1 boundary (R1.a/R1.b/R1.c) | pass |
| 2 | Forbids immediate implementation unless separately authorized | pass |
| 3 | Frozen surface spec is a required pre-existing INPUT, not a deliverable | pass |
| 4 | Forbids implementer authoring/mutating/normalizing/amending/freezing spec | pass |
| 5 | Requires fail-closed `blocked_missing_*` / `blocked_candidate_authored_*` verdicts | pass |
| 6 | Requires balanced metrics (P+R / F-beta / cost-weighted / explicit balanced) | pass |
| 7 | Forbids recall/precision/coverage/specificity/abstention/size-only admission | pass |
| 8 | Requires callable, provenance-recorded, verdict-consumed controls + size sweep 0..N | pass |
| 9 | Requires `rejected_metric_degenerate` on degenerate/size-only ceiling-band reach | pass |
| 10 | Requires positive, fail-able partial inferability (not mere absence of saturation) | pass |
| 11 | Budget-faithful visible-channel oracle only; answer-key diagnostic-only | pass |
| 12 | Baseline-immunity standard static contract only, not executor | pass |
| 13 | Provenance verifier local prefilter only, not admission | pass |
| 14 | Preserves graph-cache / leakage positive-control / replay recompute / source-pin / ablation / computed-evidence | pass |
| 15 | Touches/authorizes no source/tests/Gate/Route C/runtime/mainline/EGO path; no commit/push/tag/anchor | pass |

## Non-blocking observations

1. The drafting-task `validation_report.json` is self-reported governance shape-checking
   (`producer_function=codex_manual_validation_report`, `code_path_hash=not_applicable_manual_governance_draft`).
   Appropriate for a no-mechanism draft, but it is not fail-able evidence; this audit does not rely
   on it — the card text and the R1 chain were independently verified.
2. The amortized-learner panel entry (§15) keeps `real fitted` but drops the R1 card's explicit
   `not a deterministic stub` qualifier. Substance is preserved, but given the ACSB-001B history
   (deterministic "learned" baselines with `ml_library_used=False`), the future implementation
   should re-instate an explicit anti-stub guard.
3. §5 drops the superseded original-card hostile-audit pointer in favour of the R1 re-audit
   boundary. Reasonable supersession; the future implementation should still be able to reach the
   original audit when preserving prior negative evidence.
4. `source_readback.json` hashed only the 4 R1-boundary trigger files, not the 8 read-only
   negative-evidence inputs (those are deferred to the future implementation). Consistent with
   drafting scope; the future implementation must read + hash all of §5 via authoritative file APIs.
5. The surface spec still does not exist and no freezing authority is named (carried from the R1
   re-audit). Correct for the card, but it is the hard gating precondition for any implementation.

## Standing blocker (unrelated to this card)

Per prior audits, `scripts/push.*` hardcode a PAT; push/tag/remote-anchor must remain blocked until
the secret is rotated. This card forbids remote anchoring anyway. This audit performed no
staging/commit/push/tag/anchor.

## Next minimal closed-loop action

An independent authority (not the future preflight implementer) produces and freezes a
candidate-free surface specification pack with all §6/§11 fields, records its
path/SHA256/author/freeze-pointer/readback-channel, and obtains explicit operator authorization.
Only then may a separate Codex implementation task run the preflight against it — failing closed
(`blocked_missing_candidate_free_surface_spec`) if the spec is absent, and
(`blocked_candidate_authored_or_mutated_surface_spec`) if the implementer touches it.

## What this does not prove

That any real Gate1 replacement surface is admissible; that the future preflight will be fail-able
when implemented; that a frozen surface spec exists or is well-formed; or any Gate1 pass, mechanism
validity, candidate success, baseline-immunity enforcement, Gate4/Gate5 readiness, runtime/mainline
readiness, agency, autonomy, consciousness, emotion, stable user benefit, or EGO readiness.

## Delivery

`artifacts/CLAUDE-INDEPENDENT-GATE1-REPLACEMENT-PREFLIGHT-00XA-IMPLEMENTATION-CARD-HOSTILE-AUDIT-001A/`
(`audit_result.json` + `audit_report.md`). Not staged, not committed, not pushed, not anchored.
Pre-existing dirty worktree left untouched.
