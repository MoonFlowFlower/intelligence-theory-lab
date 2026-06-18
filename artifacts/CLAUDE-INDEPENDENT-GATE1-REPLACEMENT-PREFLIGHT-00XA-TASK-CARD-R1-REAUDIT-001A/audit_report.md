# R1 Re-Audit — GATE1-REPLACEMENT-PREFLIGHT-00XA-TASK-CARD-R1

**Date:** 2026-06-17
**Auditor:** independent red-team / same-agent-bridge-audit-role-001 (card-level)
**Target:** `artifacts/gate1_replacement_preflight_00xa_task_card_r1/draft_next_task_card_r1.md` (527 lines)
**Prior verdict:** `requires_one_bounded_task_card_repair` (blocker = Q6 metric degeneracy / R1.a)

## Verdict

**`r1_accepted_for_implementation_card_drafting`**

- Implementation may proceed now: **false**
- Only implementation-card drafting authorized (not Gate implementation): **true**
- Remaining blocking issue: **none**

## Scope

Audited **only** whether the three required repairs (R1.a, R1.b, R1.c) are satisfied. Did **not** evaluate Gate1 admissibility, mechanism validity, candidate success, baseline-immunity enforcement, runtime readiness, or EGO readiness.

Identity: repo and uploaded copies are byte-equivalent in content; read via file-API (not bash), clean close at L527, no FUSE tail-truncation artifact.

## R1.a — Metric degeneracy explicitness — SATISFIED

The prior blocker was that metric shape was delegated to one by-reference sentence ("any degeneracy trigger from the standard fires") instead of being operationalized — the exact pattern behind the Route C separation-probe false positive (recall-only, no precision penalty → `predict_all` = oracle = 1.0).

The card now operationalizes it with dedicated sections:
- **Balanced Metric Requirement** (L204-211): must report precision+recall jointly, F-beta with stated beta, cost-weighted utility with FP/FN costs, or another explicitly balanced metric.
- Explicit single-sided forbid list (L213-221): recall/precision/coverage/specificity/abstention/size-only — all six named, barred as admission basis.
- **Size-Only Sweep** (L242-253): vary set size 0..N, content policy held/matched, reject if score climbs to ceiling by size alone.
- **Control Consumption** (L256-261) + **No By-Reference Escape** (L263-270): controls must be computed, provenance-rowed, and consumed by final verdict; citing the standard is explicitly declared insufficient. `rejected_metric_degenerate` is bound at L224/L239-240/L251-253 and in the Acceptance Gate (L426-429).

## R1.b — Positive admission basis — SATISFIED

- Admissibility explicitly cannot be framed as "baselines did not saturate" (L274-276).
- **Partial-Inferability Demonstration** (L278-299) requires all of: passive observation does not trivially decode the target; target not info-theoretically independent of fair channels; genuine residual uncertainty; legal channel can reduce it in principle.
- Required controls (L289-295): passive-only attacker family, visible-channel decodability check, random/matched marginal baseline, non-reading/null oracle negative control that cannot reach ceiling, fail-closed if fair channel has no signal.
- **Budget-Faithful Visible-Channel Oracle** (L301-317): budget-faithful, visible-channel only, legal-access only, no hidden answer key, no planted truth, not presupposing the mechanism, must clear strongest fair baseline by ≥ equivalence band. Answer-key oracle is diagnostic-only, never admission support.

## R1.c — Surface spec authorship / immutability — SATISFIED

`Surface Specification Authorship And Immutability` (L89-110): spec must exist before implementation; implementer must not author/mutate/amend/normalize/freeze it; must be frozen by a separate authority or be a pre-existing accepted artifact; implementation must record path, SHA256, author/source, freeze timestamp or decision-log pointer, and canonical readback channel. Two blocking verdicts defined and listed in allowed verdicts: `blocked_missing_candidate_free_surface_spec` (L86, L104-105) and `blocked_candidate_authored_or_mutated_surface_spec` (L87, L106-107).

## Cross-cut discipline

Claim ceiling held (L33, L513-518). No implementation/scope creep. No governance self-modification — the baseline-immunity standard and registry are referenced as static contracts, not executors (L269-270, L319-326). No regression: all prior strengths preserved (no old-Gate1 inheritance; six graph-cache challengers stop-bound; computed-evidence gate; verifier-prefilter-only; leakage/replay/source-pin discipline; terminal stop; candidate-card-drafting ceiling). The new oracle clause actively reduces leakage risk.

## Non-blocking observations (no fix required for acceptance)

1. The surface-spec dependency targets an artifact that does not yet exist and names no specific freezing authority. Correct for the card's claim ceiling, but R1.c's protection only holds in practice if that spec is genuinely produced and frozen by an independent authority before the implementation card runs. Downstream tracking item.
2. Stop Condition L462 still carries the by-reference trigger; now additive/harmless because operationalized triggers (L460-465) and No-By-Reference-Escape (L263-270) sit alongside it.
3. Numeric equivalence band / metric thresholds are deferred to the frozen surface spec (correct), so the future implementation-card audit must confirm they were not chosen post-hoc.

## Claim ceiling

Accepting this card authorizes **only** drafting of the next Codex implementation card. It is not Gate1 admissibility, not mechanism validity, not candidate success, not baseline-immunity enforcement, not runtime/EGO readiness, and produces no Gate evidence.

## What this does not prove

That any real Gate1 replacement surface is admissible; that the future preflight will actually be fail-able once implemented; that an independently frozen surface spec exists or is well-formed; any mechanism, candidate, consciousness, agency, autonomy, or EGO claim.

**Delivery:** this bundle only. Not committed, not pushed, not anchored.
