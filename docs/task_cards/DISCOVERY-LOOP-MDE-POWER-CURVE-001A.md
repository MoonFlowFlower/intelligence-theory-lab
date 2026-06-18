# Task Card — DISCOVERY-LOOP-MDE-POWER-CURVE-001A

**Status note:** self-authored AND self-executed by Claude at operator instruction ("同意最优修复,
修复后进行5"). Conclusion needs an independent hostile audit before use. Pre-registration frozen
before any result was seen. Successor to DISCOVERY-LOOP-IDENT-CALIB-001A.

## task id
DISCOVERY-LOOP-MDE-POWER-CURVE-001A

## research layer
engineering_implementation + mechanism_hypothesis (tool calibration / power analysis).

## problem definition
001A showed the discovery loop's "equivalence/collapse" verdicts are POWER-LIMITED: a world with a
genuinely necessary latent (true gap ~0.007 nats) was reported "equivalent" at L_train=3000. The
agreed fix (#4) is that every negative/collapse verdict must carry a **power statement** — the
minimum true effect size it could have detected at its data budget. This task BUILDS that primitive
(minimum-detectable-effect, MDE) and then USES it (#5) to chart how the detection floor moves with
the training budget (the power curve).

## current stage
Phase-0 tool calibration / power analysis (candidate-free). Reuses 001A's loop unchanged.

## hypothesis
H: The loop's MDE (smallest true latent advantage it detects with power ≥ 0.8) is finite and
**decreases as L_train increases** (more data lowers the floor). The 001A miss (p_stay=0.95 @ L=3000)
will sit below MDE(3000); the 001A separation (p_stay=0.97 @ L=3000) at/above it.

## system / effect-size knob
- Worlds = 2-state persistent HMM, emission fixed P(o=1|s=1)=0.80, P(o=1|s=0)=0.20 (the 001A
  latent_necessary family), parameterized ONLY by persistence p_stay. Higher p_stay → longer memory
  → larger true latent advantage over any finite-order count table.
- true_gap(world) [ORACLE, effect-size DEFINITION, not a model-under-test]: with the TRUE generative
  params, on a large held-out (L=20000): true_gap = best_order_k_count_table_loss − true_HMM_loss.
  This is the asymptotic latent advantage. Using true params here DEFINES the effect size; it is
  never passed to the fitted loop.
- Fitted loop = IDENTICAL to 001A (order-k count table baseline, EM-HMM, causal one-step held-out
  log-loss, ε=0.01). n_states FIXED to 2 because 001A's BIC selection chose K=2 in 40/40 cells
  (behaviorally identical, halves cost; verified from 001A trace.csv).

## baseline
Same as 001A: strongest observation-only order-k count table (best held-out k). The latent model
must beat it by ε to "separate".

## ablation / controls (fail-able)
- C1 monotone-in-effect: at each budget, fitted power must be non-decreasing in true_gap (Spearman
  ≥ 0 with ≤1 inversion). Fail → `check_effect_knob_not_monotone`.
- C2 monotone-in-budget: MDE(L) must be non-increasing in L within tol=0.002. Fail →
  `check_power_curve_nonmonotone`.
- oracle sanity: largest-p_stay world must have true_gap > smallest-p_stay world (knob orders effect).
- tie-back (reported, non-gating): at L=3000, power(p_stay=0.95) and power(p_stay=0.97) vs 001A.

## trace / replay requirement
- trace.csv: one row per (p_stay, L_train, seed): true_gap_world, fitted gap, separates.
- power_curve.csv/json: per (L_train): per-world power, MDE.
- replay: recompute per-(world,L) power and MDE from trace.csv only; replay MDE must equal result MDE.

## acceptance gate (PRE-REGISTERED — frozen)
Constants:
- p_stay worlds = {0.85, 0.92, 0.95, 0.97, 0.99}; emission 0.80/0.20 fixed
- L_train budgets = {1500, 3000, 6000}; L_heldout = 3000 (fixed; only TRAIN budget varies)
- orders = {0..4}; hmm_n_states = 2 (fixed); em_restarts = 3; em_iters = 40; em_tol = 1e-4
- ε = 0.01 nats (SAME loop as 001A); seeds = 0..9 (10); power_threshold = 0.8 (≥8/10)
- oracle big_L = 20000; C2 tol = 0.002
MDE(L) = true_gap of the lowest-true_gap world reaching power ≥ 0.8 at budget L (smallest detectable
effect). If none reach 0.8 → MDE = ">max_true_gap_tested"; if all do → "<min_true_gap_tested".
Verdict: C1 fail → `check_effect_knob_not_monotone`; else C2 fail → `check_power_curve_nonmonotone`;
else → `power_curve_estimated__mde_decreases_with_budget` (PASS) + MDE table + power_statement(L).

## claim ceiling
Bounded power analysis of the 001A discovery loop on a 2-state-HMM effect-size family (binary
alphabet, emission 0.8/0.2). Produces MDE(L) — the minimum true latent advantage the loop detects at
budget L — and a reusable power-statement primitive. NOT consciousness/subjectivity/etc. NOT
interventional. The MDE values are specific to this alphabet/model/family; other settings differ.

## stop condition
Stop + report failure on: secret non-clean; replay MDE ≠ result MDE; C1 or C2 fail (report the
check_* verdict as-is). Do NOT change ε, p_stay grid, L grid, threshold, or tol after seeing results.

## rollback plan
New files only: `src/discovery_loop_mde_power_curve_001a/*`, `tests/test_…001a.py`,
`docs/task_cards/…001A.md`, `artifacts/DISCOVERY-LOOP-MDE-POWER-CURVE-001A/*`, and a PROPOSED (not
applied) amendment draft under that artifacts dir. No existing file modified; 001A artifacts
untouched; the baseline-immunity-admission-standard is NOT edited in place (governance: amendment is
a draft requiring operator authorization). No remote push.

## anti-hardcoding commitments
Oracle true params define the effect size only and never reach the fitted model; loop config frozen
and identical to 001A; ε/grids/threshold frozen here; n_states=2 justified by 001A selection;
causal/past-only; replayable from trace; monotonicity controls are fail-able.
