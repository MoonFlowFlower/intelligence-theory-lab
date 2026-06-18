# PROPOSED AMENDMENT (DRAFT — requires operator authorization)

**Target standard:** `docs/BASELINE-IMMUNITY-ADMISSION-STANDARD-001A` (and `.registry.json`)
**Status:** DRAFT proposal. NOT applied. Editing a governance standard is governance
self-modification and must be authorized + independently audited first. This file only proposes text.
**Evidence basis:** DISCOVERY-LOOP-IDENT-CALIB-001A + DISCOVERY-LOOP-MDE-POWER-CURVE-001A.

## Why
001A: the loop's "equivalence/collapse" verdicts are power-limited — a genuinely-necessary latent
(true_gap ~0.007) was reported "equivalent" at L=3000. MDE-power-curve: the floor is **not** lowered
by more data; for a latent model vs a flexible (consistent) observation-only baseline, separation is
governed by whether the **asymptotic** gap exceeds the band ε. Worse, a separation seen only at small
data can **evaporate** with more data (baseline-underestimation artifact).

## Proposed clause A — Power statement required on every negative/equivalence verdict
A negative / baseline-equivalence / collapse verdict is INADMISSIBLE as evidence unless it carries a
**power statement**:
1. the band ε (or equivalent decision threshold) used;
2. an estimate or bound on the **minimum detectable asymptotic effect** the test could have caught at
   its data budget (e.g., via a known-truth effect-size sweep, or an analytic bound);
3. an explicit statement that the equivalence rules out only effects **above** that floor.

A negative without (1)–(3) is ambiguous between "truly equivalent" and "real effect below the floor"
and MUST NOT be read as non-identifiability.

## Proposed clause B — Floor is not a data-budget problem for flexible baselines
Do NOT assume "collect more data" lowers the floor. When the baseline class is a *consistent*
estimator that can approximate the candidate's process (e.g., high-order count table approximating an
HMM), more data shrinks the candidate's measured advantage toward a possibly sub-ε asymptotic gap.
The admissible reading is set by the **asymptotic** gap vs ε, not by budget.

## Proposed clause C — New killer family: small-data baseline-underestimation separation
Add to the failure-family registry:
> **small_data_underestimation_separation**: a separation that appears at small training data and
> shrinks/evaporates as the budget grows (the gap converges down toward a sub-ε asymptotic value
> because the baseline was under-estimated, not because the candidate is truly better). A separation
> claim MUST be shown **budget-robust** (persists or grows with more data) before admission.

## Acceptance gate for adopting this amendment
- independent hostile audit of both source tasks;
- confirmation the killer-family addition does not collide with existing families;
- operator authorization to edit the standard + registry.

## What this proposal does NOT claim
Not that data never helps (a fixed weak baseline differs). Not a universal MDE. Not consciousness/
subjectivity. The boundary-world power estimate in the source run is EM-variance confounded; the
clause text relies only on the robust conclusions.
