# FSP-PUM-ENV-IDPROBE-001A — S3d Battery Interpretation Pre-Registration 001A

Status: **PRE-REGISTRATION. Must be banked (frozen) BEFORE the S3d battery is launched**, so it
predates any battery result. Author: Claude (independent auditor), 2026-07-04. Derived from this
session's `c0c6bf4` (001B-IMPL) audit + the 22.297 CPU-h variance-check.

## What this card IS / IS NOT

- IS: a **claim-ceiling / interpretation** pre-registration. It fixes, in advance, how three
  parts of the battery outcome may and may not be described at audit time.
- IS NOT: a change to any pass/fail rule. All thresholds, the 18-member set, cert cells, ρ
  thresholds, NULL MDE, and the k=5 validity guard remain **exactly** as in the frozen
  `S3D-SHOULD-WIN-NULL-ENV-SPEC-001A/001B` and `S3D-BATTERY-EXEC-001A`. This card cannot make a
  spec-pass into a fail or a spec-fail into a pass. It only **bounds the claim** attached to a
  spec outcome.

## task id
`FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-INTERPRETATION-PREREG-001A`

## Predicted evidence geography (pre-registered before results)

The battery has 6 should-win cells. Their audit weight is **not** uniform. Pre-registered split:

**Discriminative cells (where real should-win mechanism evidence can accrue).** Genuine
ideal-over-challenger headroom on the canonical scorer, from `s3d_001b_impl_report.json`:
- `camouflage_off`: ideal 0.0966 vs obs-decoder members ~0.052 / 0.079 / 0.051.
- `low_diversity`: ideal 0.2415 vs strongest challenger `nearest_neighbor_user_matching` 0.1205
  (all graph-cache challengers ≤ 0.12).
- `flat_theta`: ideal 0.1260 vs members ~0.031–0.032.
The substantive weight of any battery pass rests **here**.

**N2 — constant cells are baseline-saturated degenerate controls (NOT mechanism evidence).**
`degenerate_should_win_constant_none` and `degenerate_should_win_constant_saturated` have ideal
= **1.0**, which **ties trivial baselines**: for `constant_none`, `predict_none` = `majority` =
`global_prior` = 1.0; for `constant_saturated`, `predict_all` = 1.0 (`ideal_sanity_canonical_table`,
`ideal_gte_member` holds only as a tie). Per `BASELINE-IMMUNITY-ADMISSION-STANDARD-001A`
(predict_all / predict_none / majority saturation invalidates a mechanism claim), a ρ-pass on
these two cells is **instrument-control evidence only**. At audit these cells may be described as
"the ideal correctly reaches 1.0 on a constant environment" — they may **not** be counted as
should-win *mechanism* wins, because a trivial baseline equals the ideal. The k=5 validity guard
(ideal − chance ≥ k·SE) passes them trivially (Δ 0.969 ≫ 0.013); passing that guard means the cell
is above chance, **not** that it discriminates mechanism from a trivial baseline.

**N3 — `rag_should_win_stable_facts` is instrument-fragile (weak-evidence ceiling).** Its deciding
metric (recommend-turn-conditional) is scorer/sample dependent: **0.0** (one-user regression) →
**0.05864** (old inline diagnostic, k=10 fractional sample) → **0.13631** (canonical, k=15 pooled
macro-balanced accuracy). Only the canonical value clears the guard, and only by **0.00718**
(Δ 0.10506 vs k·SE 0.09788) on **n = 79** recommend turns; the should-win member `rag_k5` (0.11387)
sits just under the ideal (0.13631). Per `MECHANISM-SIGNATURE-VERDICT-STANDARD-001A`, this is
pre-registered as **predicted-fragile geography**: a green here is **low-confidence** evidence,
must be reported *with* its scorer dependency and n=79, and may **not** be upgraded to strong
mechanism evidence regardless of the ρ value it attains.

**N1 — evidence-provenance (replayability) constraint.** The 001B-IMPL verification tables were
produced by an ephemeral driver (`s3d_001b_impl_generate_report_tmp.py`, not committed / not on
disk) — a replay-contract weakness. The battery must **not** repeat this. Battery evidence counts
only if produced by the committed `artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_battery_runner_line30.py`
entry point at HEAD, with `producer_function` fields citing committed runner functions, and the
verdicts replayable from the committed `trace.jsonl`. Any number sourced from a temp/inline driver
is **not** admissible battery evidence.

## How this binds the battery audit

At battery-audit time (next session), the auditor MUST:
1. Confirm N1: every headline metric's `producer_function` is a committed runner function; replay
   reconstructs verdicts from committed trace. If any headline number came from a temp driver →
   provenance BLOCKER.
2. Apply N2: report constant-cell outcomes as control-only; strike any wording that calls them
   should-win mechanism evidence.
3. Apply N3: report `stable_facts` as fragile, scorer-dependent, n=79; cap its contribution at
   low-confidence.
4. Anchor mechanism-strength claims on the discriminative cells (camouflage_off / low_diversity /
   flat_theta) only.

## Claim ceiling (of this card and of any battery pass it governs)

A battery pass certifies, at most: **bounded S3d should-win + NULL-env instrument evidence under
the frozen contract at line L=30, carried by the discriminative cells; with constant cells as
degenerate controls and stable_facts as fragile.** It does NOT establish environment validity,
baseline-power, headroom-as-mechanism, gap, mechanism, learning, agency, self-awareness, autonomy,
EGO/companion readiness, or the correctness of any theory (Bio-CMBC / CVPSM / VCCO / CMBC / R/G).

## Freeze / operator acknowledgment (bank before launch)

```
Pre-registration acknowledged (N1/N2/N3 bind the battery interpretation):  [X] yes
Confirm this card changes NO pass/fail threshold (interpretation only):    [X] yes
Operator: ___________Leo_________   Date: ______26/7/4______
```
Bank this card (scoped commit, no push) BEFORE the battery runs. If banked after the battery
result exists, it is no longer a valid pre-registration and its N2/N3 constraints must instead be
applied as post-hoc caveats (weaker).
