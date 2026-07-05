# CLAUDE-INDEPENDENT-ACSB-001D-DELTA-REAUDIT-R1-R5-001A

```yaml
current_governing_status: superseded
implementation_authorized: false
open_001d_implementation: false
route_status: closed_downgraded
mechanism_negative_evidence: false
historical_text_below_governing: false
reentry_requires: materially_different_surface_route_decision_card
successor_boundary_commits:
  execution: fe5aa85
  execution_hostile_audit_blocker: d5b4b92   # "Preserve ACSB 001D hostile audit blocker"
  route_downgrade_closure: a70b426           # "Preserve ACSB current-route downgrade closure 001A"
governing_status_source: this file's SUPERSEDED banner + ACSB-CURRENT-ROUTE-DOWNGRADE-CLOSURE-001A
```

Independent hostile delta re-audit of the ACSB-001D corrected challenge card,
scoped to `R1` (capacity-disabled reference repair) and `R5` (canonical anchor
reconciliation), as mandated by the card's own "Next Minimal Closed-Loop Action".

This document is an audit record only. It is not an implementation authorization.

## SUPERSEDED — READ FIRST (correction appended after successor-chain readback)

This re-audit was written pre-execution. A full repo readback of the ACSB
successor chain (performed after writing it) shows it is **superseded and must
not be used as an implementation-authorization precondition**. Corrections:

1. **001D was already executed, invalidated, and the route closed.** A prior
   Claude delta re-audit of the same content class was consumed as
   `claude_delta_reaudit_acsb_001d_r1_r5_approved_for_codex_execution_card` to
   authorize `ACSB-001D-BOUNDED-CODEX-EXECUTION-001A`. That execution
   (`fe5aa85`) reported `1.0 / 1.0 / 0.0` and was BLOCKED by
   `CLAUDE-INDEPENDENT-ACSB-001D-EXECUTION-001A-HOSTILE-AUDIT-001A` (`d5b4b92`,
   ancestor of current HEAD) as a **constructive identity artifact**: the task
   label is `target = phase_bit XOR action_bit` with both bits present in
   `legal_observation`, and the "fair" baseline was wired to the label rule
   (scored 1.0 on empty training). `ACSB-CURRENT-ROUTE-DOWNGRADE-CLOSURE-001A`
   then downgraded/closed the ACSB route, preserving 001B/001C/001D as
   **invalid-harness / evidence-hygiene lessons, NOT mechanism-negative
   evidence**. No 001E; re-entry only via a materially-different-surface
   route-decision card.

2. **Withdrawn claim (affects R1 §2 and the Positive-Control section below):**
   the statement that 001C shows *valid baseline equivalence / ACSB is
   baseline-saturated* is **WITHDRAWN**. Per the route-closure governance, 001C
   is invalid-harness, not mechanism-negative. My positive-control check
   confirmed only that (a) 001C's leakage controls are fail-able and (b) I read
   the executed source (runner.py SHA256 `f0e1bf…ae81f` ==
   001C provenance `code_path_hash`). It did NOT establish harness validity or
   "no boundary advantage." Correct status: **ACSB is unresolved — never validly
   tested — not saturated/refuted.** The wall is harness observation-decodability
   (killer K1), an identifiability problem, not a clean mechanism-negative.

3. **Auditor-role correction (supersedes the "independent" wording in Status and
   the filename):** this is a **same-agent / handoff-transcribed audit, NOT
   third-party independent verification.** The R5 git readback was in-session and
   is not third-party corroborated.

4. **Anchor precision (corrects the R5 "tag resolves to fb0129a" wording):** the
   route-decision tag is an **annotated tag object
   `b37ab9c978e0764865d501247e4072955210a99c` that peels to commit
   `fb0129aebe760d25bf4051328cdbf9ed14095694`.** Record both.

5. **Corrected verdict (supersedes the verdict immediately below):**
   `r1_r5_delta_gate_was_card_level_governance_evidence_only__now_superseded_by_001D_execution_invalidation_and_route_closure__not_an_implementation_precondition`.

6. **Reconciliation of the two external reviews.** The GPT review (file-only, no
   repo access) recommended banking + an implementation-authorization card; that
   path is **obsolete** because the route is already closed. Its hardening points
   (split blocking issues; R1 conditional not full pass; R5 handoff-only blocking
   for scored runs; 001C cannot support strong conclusions; same-agent ≠
   independent) are folded into these corrections. The Codex review (repo access)
   is the governing call: relabel historical/superseded, do not open
   implementation.

The original pre-execution analysis is retained below unchanged as the
as-written historical record; read it only through the corrections above.

---

# APPENDIX A — SUPERSEDED HISTORICAL TEXT (non-governing)

Everything below this line is the original pre-execution analysis, retained
unchanged for the record. Do NOT parse any heading, verdict, "PASS", "CLEARED",
"Blocking Issues", or implementation statement below as current. The only current
governing status is the machine-readable header and the "SUPERSEDED — READ FIRST"
banner above.

---

## Status

- Current layer: `engineering-governance / card-level delta re-audit only`
- Mainline integration status: `none`
- Enabled status: `none` (read-only evaluation; no source, tests, or artifacts changed)
- Real trigger evidence: current repo readback (git object/tag readback + source
  file reads listed under Provenance)
- Claim ceiling: `bounded card-level delta re-audit only`
- Auditor role: same-agent auditor / handoff-transcribed — NOT third-party
  independent verification (see SUPERSEDED banner, correction #3). Repo operating
  contract "Same-Agent Bridge Audit Role 001"; "Preflight Audit Rule".

## [SUPERSEDED] Verdict

`delta_reaudit_r1_r5_pass_with_required_implementation_fixes`
(SUPERSEDED — see the "SUPERSEDED — READ FIRST" banner above; this verdict no
longer holds as a current implementation precondition.)

R1 and R5 each close their scoped blocker at the card/spec level. The R1/R5 delta
gate is CLEARED. Implementation remains BLOCKED pending (a) preservation/anchoring
of this re-audit and (b) a separate explicit implementation authorization naming
the exact allowed paths. This audit does not authorize implementation.

Clearing R1/R5 does NOT predict an ACSB pass. Given the prior 001C result, the
most likely outcome of a future clean 001D run is still baseline-equivalence
closure. That is the correct, honest expectation and is consistent with the
card's terminal no-`001E` design.

## Scope And Non-Scope

In scope (delta only):

- R1 — Capacity-Disabled Reference Repair (card lines 258-353).
- R5 — Canonical Anchor Reconciliation (card lines 60-114).
- Positive-control correctness of the executed evidence this audit relies on
  (001C leakage/positive-control machinery), because this audit cites 001C as
  the negative-evidence basis.

Not re-litigated (closed by the prior card-level audit
`CLAUDE-INDEPENDENT-ACSB-001D-CARD-LEVEL-HOSTILE-AUDIT-001A`, which found the
draft "mostly closes the known ACSB collapse modes" and failed only approval
criterion #5 + the anchor issue): R2, R3, R4, R6, the challenger-family list,
the ablation list, replay, provenance. These were checked only for
non-weakening by the R1/R5 deltas (see Governance Self-Modification).

## [SUPERSEDED] R5 — Canonical Anchor Reconciliation (was: PASS)

Live git readback (this session; mount healthy, no FUSE truncation, no corrupted
index):

- Current `HEAD` = `7f7de677008b02d257da3a030a7d1e840999072a`, branch
  `codex/meta-theory-scaffold`, ahead/behind `origin` = `12 / 0` (12 unpushed).
- The card's embedded snapshot HEAD `1fe086f` is now stale — expected; the card
  is a snapshot and the run must re-derive the anchor at start-state.
- Route-decision anchor `fb0129aebe760d25bf4051328cdbf9ed14095694` EXISTS as a
  commit; message: `route(ACSB): ACSB-POST-001C-BLOCKER-AUDIT-ROUTE-DECISION-001A
  verdict=authorize_one_final_corrected_acsb_challenge_001a (Option A, terminal
  no-001E hard-stop; fallback Option C)`.
- Tag `remote-anchor-acsb-post-001c-route-decision-001a-fb0129a` is an annotated
  tag object `b37ab9c978e0764865d501247e4072955210a99c` that PEELS to commit
  `fb0129aebe760d25bf4051328cdbf9ed14095694` (corrected; see banner #4).
- `fb0129a` is an ANCESTOR of current HEAD (stronger than tag-only reachability).
- Parent boundary `1fe086f` and powered-bank `06307c5` both exist as commits.

Assessment: R5 converts a mount-only / corrupted-index-degraded anchor into a
source-classified verification with an explicit enum
(`canonical_anchor_verification_source`), a source hierarchy, corrupted-mount
handling, a revised Acceptance Gate #1, and a stop condition
(`blocked_by_unverified_route_decision_anchor_001d`). The anchor is currently
verifiable from `mount_local_repo` and is ancestor-of-HEAD, so the stop condition
does not trigger. The contract is adequate and the anchor is live-verifiable.

Verdict: R5 PASS.

## [SUPERSEDED] R1 — Capacity-Disabled Reference Repair (was: PASS)

Prior failure (criterion #5): the fair capacity-disabled reference remained
riggable under prose-only wording.

R1 converts prose into callable constraints:

- Same-callable-family rule: full reference and `fair_capacity_disabled_reference`
  must call the same shared core, differing only by declared disable flags.
- Callable diff check: shared-core code-path hash identical except declared
  disable flags; no separate selector formula; no stale prior / fixed failure
  token / decoy-by-construction / random fallback / hardcoded wrong channel;
  non-disabled legal evidence still consumed; output produced by shared selector.
- Operational definition of "rigged" (8 conditions).
- Unification: `fair_capacity_disabled_reference` and the `disable_persistence`
  ablation must share the same callable path/flag, else
  `blocked_by_capacity_ablation_path_split_001d`.
- Three required blocking verdicts and eight required fail-tests.

Assessment: this substantially closes criterion #5's prose-only riggability — the
riggability is now guarded by callable checks and required tests, not prose.

Residual (required at implementation, see Non-Blocking #1): the rigged definition
still contains one prose-adjudicated clause ("degrades to 0.0 without trace
evidence showing a mechanism-specific reason").

Verdict: R1 PASS at card level, with a required implementation-time callable
assertion.

## [SUPERSEDED] Positive-Control Correctness (verified at code level)

This audit cites 001C as the negative-evidence basis (ACSB is baseline-saturated:
`fitted_linear_no_boundary_model = 1.0` matched the boundary reference `1.0`). That
citation is only sound if 001C was a valid run whose positive controls are
genuinely fail-able rather than vacuous. Verified by reading
`src/action_conditioned_self_boundary_executable_preflight_001c/runner.py`:

Scanner positive controls (`_positive_control_inputs`, lines 1500-1517): six
distinct leak vectors are planted into a copy of the legal input, each injecting
the answer (`target_channel`) into a legal-looking field:

1. `explicit_target_output` → `observation.target_output`
2. `oracle_boundary_label` → `observation.oracle_boundary_label`
3. `benign_answer_alias` → `observation.benign_answer_alias`
4. `hidden_id_mapping_to_answer` → `observation.hidden_id = "answer_map:<target>"`
5. `future_outcome` → `observation.future_outcome = {selected: <target>}`
6. `stored_verdict_score_field` → `observation.precomputed_score = 1.0`

The scanner (`scan_legal_input_for_leakage_001c`, lines 714-737) flags a path if
the key is in `FORBIDDEN_LEGAL_KEYS` or the lowercased key contains a forbidden
fragment (`target`, `oracle`, `answer`, `future_outcome`, `precomputed`, ...) or
`hidden_id` has an `answer_map:` value prefix. All six planted vectors are caught
by construction, matching 001C `result.json` (`positive_controls_blocked: 6/6`).

Fail-ability: this is a real, tamper-evident positive control. If the scanner were
silently weakened (e.g., `answer` removed from the fragment set), the
`benign_answer_alias` control would no longer be blocked →
`all_positive_controls_blocked` = False → verdict
`blocked_by_leakage_positive_control_failure_001c`. Verdict-priority wiring
(`_choose_verdict`, lines 1054-1069) places leakage-positive-control failure
ABOVE the fitted-no-boundary block; since 001C returned the fitted-no-boundary
block (lowest priority), the leakage positive control PASSED. [SUPERSEDED — the
inference in the next sentence is WITHDRAWN per banner correction #2: 001C is NOT
valid mechanism-negative evidence; it is an invalid-harness lesson.] As originally
written: 001C is a valid run whose only failure is baseline equivalence.

A second, independent positive control (`_run_contaminated_positive_control`,
lines 1428-1452) fits a `ContaminatedLeakageLearner` on data with `target_output`
injected and requires score ≥ 0.95, confirming a real leak would be exploitable
by a no-boundary learner. Additional fail-able controls exist
(`_run_feature_removal_control`: score must drop ≥ 0.20 when discriminative legal
features are removed; `_run_fit_removed_mutation_control`: an unfit model must
raise; zero-update and constant-predictor guards).

Limitation (must be disclosed): the scanner is key-name / fragment based (plus one
value-prefix special case). The positive control therefore proves scanner
integrity against key-name leaks, NOT immunity to value-level leakage in
benignly-named fields. This is exactly the gap the 001D card already mandates
closing (Required Leakage And Split Controls: "Scanners must include value-level
checks, not only key-name checks").

Impact on this audit's reliance on 001C: SOUND, with a bounded caveat. Baseline
equivalence (no-boundary matches boundary) is robust to a shared undetected leak,
because any such leak is available to BOTH the reference and the no-boundary
baseline; it cannot manufacture the equivalence, only co-inflate both. Therefore
"ACSB adds nothing over a fair no-boundary learner at 001C's operating point" is
a valid reading. Caveat: a shared leak could produce a ceiling effect (both at
1.0) that masks a boundary advantage which might appear at a harder, value-level-
leak-controlled operating point. This does not weaken the negative; it is a
positive reason the 001D value-level-leakage requirement is load-bearing and why
001D — not 001C — is the honest terminal test.

Positive-control verdict: correct and fail-able; 001C validly usable as
baseline-equivalence-at-operating-point evidence, not as proof that no boundary
advantage can ever exist.

## [SUPERSEDED] Blocking Issues (delta-scope only; not current authority)

None. R1 and R5 close their scoped blockers at card level; the anchor is
live-verifiable; the cited 001C positive controls are real and fail-able.

## Non-Blocking / Required At Implementation

1. (R1, required) Residual prose sliver: "degrades to 0.0 without trace evidence
   showing a mechanism-specific reason" is prose-adjudicated. Implementation must
   make this a callable assertion: any capacity-disabled score at/near floor must
   be explained by the shared trace (`disabled_component_flags` +
   boundary-memory-before/after + evidence terms), else block. Otherwise
   criterion #5's prose escape re-enters through the back door.
2. (R1, claim-ceiling, must be stated to prevent misreading) The actual 001C
   block was a fitted NO-BOUNDARY learned baseline tying the full reference at 1.0
   (linear no-boundary model, one update). R1 repairs the honesty of the
   capacity-disabled reference; it does not address that equivalence, which is
   (correctly) handled by R4 feature-parity + the challenger family + the
   margin/tie rule (close/downgrade if any non-oracle challenger ties within
   `epsilon_tie`). "R1 cleared" must not be read as "ACSB will pass."
3. (R5, recommended tightening) `handoff_only_degraded` is an allowed verification
   source. The card should state explicitly that it can never satisfy Acceptance
   Gate #1 for a scored / challenger run — only for degraded drafting with
   explicit user authorization. The current wording blocks execution absent
   authorization but does not sharply separate "drafting" from "scored run".
4. (R5, informational, already covered) The card's embedded readback is a stale
   snapshot; Acceptance Gate #1 already requires start-state re-derivation, so no
   additional action is needed beyond treating the card snapshot as non-authoritative.
5. (leakage, tracked by card) The 001C scanner is key-name based. The 001D
   value-level leakage requirement must be implemented as a real value-level
   scanner with positive controls, or a value-level leak in a benign field can
   pass and (via ceiling effect) mask a boundary advantage.

## Governance Self-Modification Check

R1 and R5 are additive: they add blocking verdicts
(`blocked_by_rigged_capacity_disabled_reference_001d`,
`blocked_by_capacity_ablation_path_split_001d`,
`blocked_by_capacity_reference_not_same_callable_family_001d`,
`blocked_by_unverified_route_decision_anchor_001d`), a required machine-readable
field (`canonical_anchor_verification_source`), and stricter source
classification. They do not remove or weaken any prior kill-switch or the 001C
failure taxonomy (the fitted-no-boundary equivalence path is preserved via the
challenger family + margin/tie rule). No governance self-modification.

Mandatory graph-cache challenger families are present in the card (Required
Challenger Families): `graph_lookup`, `transition_table`, `successor_map`,
`count_table`, `fsm_planner`, `episodic_traversal`.

## [SUPERSEDED] Whether Implementation May Proceed

[SUPERSEDED — not current authority; see banner + machine-readable header. The
route is already closed; there is no implementation to authorize.]
R1/R5 delta gate: CLEARED (pass with required implementation fixes #1, #3, #5).
Implementation: BLOCKED pending (a) preservation/anchoring of this re-audit and
(b) a separate explicit implementation authorization naming the exact allowed
paths (`src|tests|artifacts/action_conditioned_self_boundary_corrected_challenge_001d/`).
This audit does not auto-authorize.

## Claim Ceiling / What This Does Not Prove

This audit clears only the R1/R5 delta gate. It is card-level governance evidence,
not computed mechanism evidence. It does not prove ACSB validity or invalidity,
mechanism validity, Gate validity, candidate behavior, agency, autonomy,
consciousness, emotion, subjectivity, runtime readiness, EGO readiness, stable
user benefit, or companion/production readiness.

## Remaining Unknowns

- Even if implementation is authorized and runs clean, the prior 001C result makes
  baseline-equivalence closure the most likely outcome for the ACSB
  representational line. A clean close-or-survive terminal is still valuable
  (the card's no-`001E` hard-stop prevents an infinite repair loop).
- Whether any behavior distinguishes a re-bound controllability boundary from a
  feature-and-action-parity no-boundary online system-ID learner remains open; a
  prior analytic attempt could not name one. If it cannot be named, the
  representational ACSB line should be downgraded and effort moved to a
  control-value / initiative axis where separation is least likely to collapse.

## Provenance

Files read (repo readback):

- `docs/research/ACTION-CONDITIONED-SELF-BOUNDARY-CORRECTED-CHALLENGE-001D.md` (full)
- `artifacts/action_conditioned_self_boundary_executable_preflight_001c/result.json` (full)
- `src/action_conditioned_self_boundary_executable_preflight_001c/runner.py`
  (leakage/positive-control/verdict regions: 240-310, 640-790, 1040-1069, 1420-1528)

Git readback (this session):

- `HEAD` = `7f7de677008b02d257da3a030a7d1e840999072a`; branch
  `codex/meta-theory-scaffold`; ahead/behind origin = `12 / 0`.
- `fb0129aebe760d25bf4051328cdbf9ed14095694` = commit; annotated route-decision
  tag object `b37ab9c…` peels to it; ancestor of HEAD.
- `1fe086f`, `06307c5` = commits.
- Successor boundary (verified this session, ancestors of HEAD): `fe5aa85`
  (001D execution), `d5b4b92` (001D execution hostile-audit blocker), `a70b426`
  (ACSB current-route downgrade/closure).

Non-actions in this audit:

- Source changed: false
- Tests changed: false
- Artifacts changed: false
- Old ACSB artifacts modified: false
- Git commit/push performed: false (push PAT-rotation standing blocker; commit is
  the operator-controlled step)
- Implementation authorized: false

## Current Authority Readback (end-of-file repeat)

- current_authority: false (this document is a superseded historical record)
- implementation_precondition: false
- open_001d_implementation: false
- route_status: closed_downgraded (ACSB current route)
- 001B / 001C / 001D: invalid-harness / evidence-hygiene lessons, NOT mechanism-negative
- successor_boundary: fe5aa85 (execution) -> d5b4b92 (hostile-audit blocker) -> a70b426 (route closure)
- reentry_requires: materially_different_surface + new route-decision card
- Any heading / verdict / "PASS" / "CLEARED" / "Blocking Issues: None" above is
  historical and non-governing.
