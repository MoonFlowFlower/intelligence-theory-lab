# CSSP-001A - CRITERION-SHADOW-SEPARABILITY-PROBE - c1 analytic closure

Layer: mechanism-hypothesis / identifiability instrument (analysis-only).
Disposition: **CLOSED_BY_BOUNDED_ANALYSIS**. Build status: **NO-CLEAR-for-build** (docs-only bank; no callable, no STEP-B, no agent). designer != self-CLEAR. Bank color: Yellow (negative/closure).
Audit: 2026-07-08 (three converged hostile rounds). Bank: 2026-07-09.

## Problem
Does there exist a criterion C that a genuine functional subject can satisfy but an equal-access, same-prior "shadow" (a computed Bayes-optimal predictor/controller given the same access) cannot - i.e. an equal-access SEPARATING criterion? CSSP-001A probes this for **c1 = held-out interventional-prediction accuracy over a fixed threshold** (accuracy of predicted P(Y | do(X=x)) on held-out do-queries).

## Core argument (why c1 is analytically decidable)
Let s* be the **equal-access Bayes-optimal decision rule under C's own loss/threshold** (for 0-1 accuracy, the posterior mode) computed on equal-access data under the same prior Pi. Any learner using the same (data, hypothesis class H, prior Pi) - including a candidate-learned model - cannot beat s* in expectation, because s* is the minimum-Bayes-risk decision under that information.

c1 is a functional of the accessible predictive distribution, so the causal-identifiability dichotomy (computable on a tiny enumerable SCM) decides it:
- **Query identifiable** => s* computes the do-query over threshold => the criterion is met by the shadow => **SHADOW_COLLAPSE** (no separation).
- **Query non-identifiable** (lies inside a Markov-equivalence class) => no equal-access learner can beat the posterior spread => the candidate also fails to clear threshold; only a **structure-handed** prior (the right answer hard-coded) passes => **INDUCTIVE_BIAS_ONLY** (smuggled structure = access, not a foothold).

Therefore **SEPARATING_EQUAL_ACCESS is unreachable in expectation for c1**. The only residual positive channel is a finite-sample inductive-bias fluke, pre-classified as **NON_FOOTHOLD**.

Note the self-defeating design symmetry: the card insists on a "computed Bayes-optimal, not trained" shadow. That choice avoids the ACBU under-training loophole (an undertrained shadow that loses for the wrong reason) and, in the same move, proves the card closes its own foothold.

## Load-bearing assumption (must travel with any cite)
The closure is **conditional on s* actually being the correct equal-access Bayes-optimal rule** under C's loss. If a candidate appears to clear the threshold, that is a **mandatory re-audit trigger** - re-check s*-optimality, access symmetry, compute-and-H match, oracle-label leakage - **not** a subject claim. This is the honest correction to a naive reading ("candidate reached c1 => separation"): reaching c1 above a shadow that was not truly Bayes-optimal only indicts the shadow.

## Hostile rounds (converged, all adopted)
- R-early: strawman-s1 removed; access tuple (data, H, Pi) frozen for BOTH candidate and shadow; K2 handled as a callable equivalence class; K1 decoder as a family not a single frame; s4-s5 training protocol frozen to block oracle; c2 marked candidate-internal.
- R3 tightening: (1) s* is C's own loss/threshold Bayes-optimal decision rule (0-1 accuracy => posterior mode), not a generic posterior predictive; (2) no swap of a Bayesian-average bound into a pointwise-impossibility claim (the residual "gate" = a hard-coded correct prior winning a fixed finite-sample SCM = handed structure = mirage, not a foothold); (3) c2 downgraded to candidate-internal sanity, so C = c1 ^ c2 with s* having no ablatable module would otherwise manufacture an "architecture-as-ticket" false separation - hence the separation verdict lands on **c1 only**.
- Three independent attempts to pry c1 open all failed: richer H (amortization moves up to the meta level, the wall rebuilds); counterfactual rung-3 (only widens the non-identifiable side); calibration (the Bayes posterior IS the optimal equal-access calibrator).

## Precise conclusion
Given any fixed finite (data, compute, prior) closure, the criterion "a true subject satisfies it but the equal-access shadow cannot" is provably non-existent. The necessary condition can only possibly hold in **fork A** - non-stationary / generated access, where "Bayes-optimal-given-access" is not a well-defined dominating object. And fork A itself yields only un-shadowable mechanism evidence; it does not cross the functional->phenomenal definitional gap.

## Relations and provenance
- Isomorphic to `docs/research/DRIFT-AXIS-CAPABILITY-ACBU-002A-CLOSEOUT-001A.md` (matched = equal-access Bayes-optimal => candidate <= baseline).
- Generalized by `docs/codex/tasks/CDAP-001A-R1.md` + `docs/research/CDAP-001A-R1-family-table.md` (bounded-criterion search CLOSED_OVER_NAMED_FAMILIES; c1 is Row 2).
- Consistent with the identifiability-ceiling memo (equal access hands the gap to the baseline; the only live axis is cross-episode / non-amortizable).
- **Resolves the in-repo provenance** for CDAP-001A-R1 rows 2 & 8 `[CONJECTURE]` cites. This bank is **additive only and does NOT modify CDAP-001A-R1**; any reconciliation of CDAP's cite tags is a separate authorized step. The cited object here is an analytic near-theorem argument, not an executed computation - downstream certificates should read it as analytic / reduction, not as an executed proof.

## Claim ceiling
See `artifacts/CSSP-001A/claim_ceiling.txt`. Bounded analytic closure of c1 under the stated framing; conditional on s*-optimality; no run; proves nothing about fork A, global possibility/impossibility, or any subject / consciousness / electronic-life claim.

## Optional future strengthening (NOT part of this bank; would need its own card)
A tiny enumerable-SCM computation of the E(D_train) equivalence-class invariance (the identifiability check itself) could upgrade this from an analytic near-theorem to a computed negative artifact. That is a separate build task (callable + independent Red-audit) and is explicitly out of scope for this docs-only bank.
