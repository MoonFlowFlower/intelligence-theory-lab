# Core-Only Hostile Audit — GATE1 Replacement Surface Spec 00XA Freeze

**Verdict:** `surface_spec_core_accepted_for_operator_authorization_consideration`

**Scope:** Only whether the frozen surface spec is usable as a pre-existing input
for a future *separately-authorized* preflight implementation. NOT judging Gate1
admissibility, mechanism validity, candidate success, runtime readiness, or EGO
readiness. Core checks only (not full governance re-audit).

- implementation may proceed now: **false**
- operator explicit authorization still required: **true**
- future implementer may mutate spec: **false**
- remaining blocking issue: **none**

## Core check results

1. **Freeze identity — PASS.** Independent bash sha256 raw-byte recompute of the
   live `.md` = `fca7e5eb…c9`, identical to the `spec_sha256` recorded in the
   freeze JSON and in `spec_hash_readback.json`. Three-way identity holds.
   `CR=0` (LF-only, no normalization ambiguity), 24588 bytes. The match against
   the externally-recorded PowerShell hash rules out FUSE-mount truncation on the
   decisive file (any missing byte would change the digest).

2. **Independence — PASS.** Author/source, source pointer (+per-file hashes),
   freeze pointer (timestamp/verdict), and canonical readback channel are all
   present. The future-implementer mutation ban (author / mutate / normalize /
   amend / re-freeze) is explicit in all three of spec, freeze JSON, and
   independence declaration, with stop condition
   `blocked_candidate_authored_or_mutated_surface_spec`. Enforcement is by hash
   freeze, not just declaration. Non-blocking: actor-level independence is
   self-declared; runtime hash recompute is the enforcement and is a
   future-execution obligation.

3. **Metric — PASS.** Macro F1 (β=1.0) with per-class precision *and* recall
   floors (0.85) for both classes, equivalence band 0.03, ceiling 0.90 / floor
   0.87. Recall-/precision-/coverage-/specificity-/abstention-/size-only
   admission all explicitly forbidden; degeneracy → `rejected_metric_degenerate`.
   Thresholds are frozen inside the hashed spec and post-hoc change is an illegal
   action. This closes the prior Route C recall-only `predict_all==oracle`
   false-positive vector.

4. **Baseline registry — PASS.** Mandatory callable-producer panel with degenerate
   controls, **all six** graph-cache challengers (graph_lookup, transition_table,
   successor_map, count_table, fsm_planner, episodic_traversal — no
   substitutions), an anti-stub guard on the trained learner, and exhaustive-query
   as a saturation-→-reject challenger. Preserves the lab's graph-cache,
   learned-baseline-invalidity, and exhaustive-query-saturation negative evidence.

5. **Partial inferability — PASS.** Positive fail-able requirements (passive not
   trivially decoding, target not independent of fair channels, residual
   uncertainty exists, legal channel can reduce uncertainty in principle) with
   explicit fail-closed routing (`rejected_trivially_decodable` /
   `rejected_no_fair_signal` / `rejected_baseline_saturated` /
   `blocked_missing_partial_inferability_demonstration`). This is the exact
   surface prior audits repeatedly blocked on, now encoded fail-closed.

6. **Oracle / leakage — PASS.** Answer-key oracle is diagnostic-only (answer-key
   headroom → rejection); only a budget-faithful visible-channel legal-access
   oracle supports admissibility. Leakage positive control is fail-able: removing
   the injected leak must remove detection, and the detection must be consumed by
   the final verdict; always-pass/single-dictionary scanners are forbidden.

7. **Claim ceiling — PASS.** Freeze verdict is freeze-only; admissibility is
   deferred and disclaimed. Operator authorization is explicitly still required.
   No positive Gate/mechanism/runtime/EGO claim (independently confirmed). The
   spec does **not** self-grade its admissibility target →
   `rejected_surface_spec_self_grading_or_claim_inflated` does not apply.

## Non-blocking observations

- `validation_report.json` is the freeze session's own shape self-validation, not
  independent; its decisive hash claim is independently confirmed here.
- Upstream source-pin hashes were out of core scope; the recorded
  `baseline_comparison.json` `4daa4c71…` matches prior-audit memory, indicating a
  genuine provenance chain.
- `strongest_known_classical_method_for_task_type` is implementer-selected
  (verify strength at execution); the broad mandatory challenger set mitigates.
- Budget 16 vs full legal action space cannot be checked now (no generator);
  exhaustive-query saturation rule is the backstop.

## What this does not prove

It does not prove Gate1 admissibility, that the future preflight will return
`admissible_for_candidate_card_drafting_only`, any partial-inferability /
baseline-immunity / mechanism / candidate result, or runtime/mainline/bridge/EGO
readiness. It does not authorize implementation.

## Next minimal closed-loop action

Operator issues an explicit, separate implementation authorization for a
candidate-free preflight that reads this frozen spec via canonical readback,
recomputes and asserts `spec sha256 == fca7e5eb…c9` before any score, stops on any
spec/freeze mutation, implements the full mandatory baseline panel as independent
callable producers, and submits execution-time evidence for a separate hostile
audit. No push / tag / remote anchor.
