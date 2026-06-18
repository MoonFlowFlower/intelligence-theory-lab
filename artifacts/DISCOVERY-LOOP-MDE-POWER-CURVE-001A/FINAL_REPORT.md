# Final Report — DISCOVERY-LOOP-MDE-POWER-CURVE-001A

Builds the agreed fix (#4 — a power statement / minimum-detectable-effect for negative verdicts) and
uses it for #5 (how the detection floor moves with training budget). Loop imported UNCHANGED from
DISCOVERY-LOOP-IDENT-CALIB-001A.

> Self-authored + self-executed at operator instruction ("同意最优修复,修复后进行5"). Needs an
> independent hostile audit before use. Pre-registration frozen before any result was seen.

## Verdict (honest, corrected)

Frozen machine verdict in `result.json`:
`power_curve_estimated__mde_decreases_with_budget`.

**This label is a pre-registration DEFECT and is NOT supported by the data** (see
`verdict_correction.json`). The pre-registered C2 gate ("MDE non-increasing in L → PASS") does not
distinguish *constant* from *decreasing*; the observed MDE was **flat at 0.0121 across all budgets**.

**Honest verdict:** `mde_flat_across_budget__floor_set_by_asymptotic_gap_vs_eps`.

**Headline finding (the opposite of the hypothesis):** for a latent mechanism competing against a
flexible observation-only baseline (high-order count table), **more training data does NOT lower the
detection floor.** Separation is governed by whether the *asymptotic* gap (oracle true_gap) exceeds ε
— not by data budget. And a separation found only at small data can **evaporate** with more data.

## Research layer
engineering_implementation + mechanism_hypothesis (tool power analysis).

## Files changed (all new, additive)
- `src/discovery_loop_mde_power_curve_001a/{__init__.py, probe.py}`
- `docs/task_cards/DISCOVERY-LOOP-MDE-POWER-CURVE-001A.md`
- `artifacts/DISCOVERY-LOOP-MDE-POWER-CURVE-001A/*` (incl. `verdict_correction.json`,
  `PROPOSED-AMENDMENT-power-statement-001A.md`)
No existing file modified; 001A artifacts untouched; the baseline-immunity-admission-standard is
**not** edited (amendment is a draft needing operator authorization); no remote push.

## Commands run
- setup (cp both packages to /tmp, strip FUSE null-padding, compile, import-check)
- full 150-cell run (5 worlds × 3 budgets × 10 seeds) via checkpointed driver
- oracle effect-size computation (5 worlds, large held-out, true params)

## Provenance
- `prereg_sha256 = 143c3cc936b6…`, `code_path_hash = e15dad3319d6…`, `secret_scan.clean = true`
- FUSE caveat (same as 001A): execution copies null-stripped before run; canonical repo sources are
  the same content; auditor should recompute hashes via a non-FUSE path.

## Results

Oracle effect size (asymptotic latent advantage over best order-≤4 count table; L=20000, true params):

| world p_stay | true_gap (nats) |
|---|---|
| 0.85 | 0.000425 |
| 0.92 | 0.002270 |
| 0.95 | 0.006832 |
| 0.97 | 0.012108 |
| 0.99 | 0.028715 |

Fitted-loop separation power P(separates), ε = 0.01:

| budget \ true_gap | 0.0004 | 0.0023 | 0.0068 | 0.0121 | 0.0287 |
|---|---|---|---|---|---|
| L=1500 | 0.0 | 0.0 | 0.5 | 1.0 | 1.0 |
| L=3000 | 0.0 | 0.0 | 0.2 | 0.9 | 1.0 |
| L=6000 | 0.0 | 0.0 | 0.2 | 0.8 | 1.0 |

MDE (smallest reliably-detected true_gap, power ≥ 0.8): **1500 → 0.0121; 3000 → 0.0121; 6000 →
0.0121** (flat; = the p_stay=0.97 world).

Mean measured gap vs true_gap (mechanism): for true_gap < ε worlds, more data pulls the measured gap
DOWN toward the true sub-ε value (p=0.95: 0.0101 → −0.001 → −0.002), so small-data separations
collapse. For true_gap > ε worlds (0.97/0.99) the gap stays above ε at all budgets → separation
persists.

Tie-back to 001A at L=3000: power(p=0.95)=0.2 (missed, matches 001A) and power(p=0.97)=0.9 (separated,
matches 001A). Consistent.

## Baseline results
Strongest observation-only order-k count table (best held-out k, k≈4). It is a *consistent*
estimator: with more data the order-4 table tightens and captures most of the latent process's
predictable structure up to order 4, shrinking the latent model's measured advantage toward the small
asymptotic true_gap. This is *why* more data hurts separation for sub-ε worlds.

## Ablation / control results
- C1 (power monotone in true_gap at each budget): **passed** (≤1 inversion per budget; effect axis valid).
- C2 (MDE non-increasing in budget): passed *trivially* (constant) — and this is exactly the label
  defect: the gate cannot tell flat from decreasing.
- oracle sanity: true_gap strictly increases with p_stay (knob orders the effect). ✓

## Confound (disclosed)
At the boundary world p_stay=0.95 the per-seed gap variance explodes at larger L (sd 0.0028 → 0.0276
→ 0.0299) with occasional large-negative gaps — partly EM-HMM instability (em_restarts=3 insufficient
at larger L), not pure gap-convergence. This affects the single boundary world's exact power value,
not the qualitative conclusions (which rest on the clean 0.97/0.99 and 0.85/0.92 worlds).

## Replay result
`replay_verdict == result_verdict` and `replay_mde == result_mde` (both True): power, MDE, and verdict
recompute exactly from `trace.csv` (separates + true_gap) alone.

## Tests run
None new for this module (the run is self-validating: C1 + oracle-ordering + exact replay in
artifacts). 001A's suite still passes. *A small unit suite for this module is a remaining to-do.*

## Anti-hardcoding self-audit
- oracle true params define the effect-size x-axis only and never reach the fitted model (label-blind
  preserved). ✓
- loop config frozen + identical to 001A; n_states=2 justified by 001A (40/40 K=2). ✓
- ε, p_stay grid, L grid, threshold, tol frozen in PREREG before run; not changed after. ✓
- **label defect disclosed, frozen verdict NOT mutated**, corrected reading recorded additively in
  `verdict_correction.json`. ✓
- causal/past-only; replayable from trace. ✓
- EM-variance confound disclosed rather than hidden. ✓

## Reshaped fix (#4) — corrected power statement
A negative/equivalence verdict's power statement is **NOT** "collect more data to lower MDE." It is:
*the loop reliably detects only asymptotic gaps > ε; effects with asymptotic gap < ε are undetectable
at ANY budget in this baseline class, and a separation seen only at small data is non-robust
(baseline-underestimation false positive) and must be re-checked at a larger budget.* See
`PROPOSED-AMENDMENT-power-statement-001A.md` (draft; requires operator authorization — not applied to
the standard).

## Claim ceiling
Bounded power analysis on a 2-state-HMM family (binary alphabet, emission 0.8/0.2) against an
order-≤4 count-table baseline. MDE values (~0.012 nats) are specific to this alphabet/model/baseline
order. Not consciousness/subjectivity/etc.; not interventional.

## What this does not prove
- Not that data NEVER helps separation in general — only for a latent model vs a consistent flexible
  baseline whose class can approximate the latent process. A *fixed weak* baseline would behave
  differently.
- Not the exact MDE for other alphabets, baseline orders, or effect families.
- Not that p_stay=0.95's power drop is purely gap-convergence (EM-variance confounded).
- Nothing about interventional identifiability or subjectivity.

## Remaining unknowns
- The floor's dependence on baseline ORDER (raising k would shrink true_gap further — likely lowers
  separability; untested).
- A clean boundary-world power estimate with more EM restarts (to remove the variance confound).
- Whether the "small-data separation evaporates" effect reproduces for non-HMM mechanism families.
