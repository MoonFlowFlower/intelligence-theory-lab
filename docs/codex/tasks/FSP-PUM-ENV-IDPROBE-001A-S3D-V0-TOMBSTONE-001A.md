# FSP-PUM-ENV-IDPROBE-001A — S3D-V0-TOMBSTONE-001A

Status: **CLOSURE CARD (route downgrade). Operator signature WAIVED per solo-efficiency policy (2026-07-05); banks via scoped commit. R2 reopen conditions below remain pre-registered and binding.**
Auditor-drafted (Claude), 2026-07-05. This card closes the S3d v0 instrument. It changes no
science code and no banked experiment artifact; it records the closure, pins the evidence, and
pre-registers the only conditions under which a successor (R2) may reopen the route.

## task id
`FSP-PUM-ENV-IDPROBE-001A-S3D-V0-TOMBSTONE-001A`

## problem definition
S3d v0 (the should-win + NULL-env certificate battery, spec `S3D-SHOULD-WIN-NULL-ENV-SPEC-001A/001B`)
is closed as an **invalid latent-mechanism gate**. Two full battery runs plus two bounded diagnostics
established that S3d v0 cannot support a mechanism claim.

## current stage
- Battery run 1 (L=30) → void, banked `d983b59` (runtime-guard boundary).
- Battery run 2 (L=38, post GRU-seed-determinism repair) → void on `FAIL_NULL_FALSE_HEADROOM`
  (this session; evidence committed with this closure).
- Diagnostic `S3D-NULL-IDEAL-DIAG-001A` (commit `30caa7f`) and `-002A` (commit `5cb90397`)
  isolated the cause.

## verdict
**`S3D_V0_TOMBSTONED`** — invalid as a latent-mechanism gate on **two independent grounds**.

### Ground 1 — instrument identifiability failure (style_map privilege / ρ conflation)
- **NULL false-headroom:** the ideal breaches the pre-registered NULL guard (§5): NULL metric
  `0.07211` > limit `0.03625` (= chance `0.03125` + pre-registered MDE `0.005`). All 18 members
  pass at ~chance.
- **Diag 001A → `RESIDUAL_ACTION_STRUCTURE_VIA_STYLEMAP` (not leakage):** predictions are history-
  and posterior-independent (both diffs `0.0`); wrong-style_map → chance; analytic `0.0722` ≈
  battery `0.0721`. The oracle decodes the action-only mode via the per-user `style_map` it is handed.
- **Diag 002A → `PRIVILEGE_RHO_WIDE`:** the oracle's score in the **real** cells is also
  style_map-gated — wrong-style_map collapses it to chance (`low_diversity` 0.324→0.021,
  `flat_theta` 0.116→0.029). The oracle is handed each eval-user's true `style_map`; members
  (fit users 0–639, eval users 640–799, disjoint) are not. Therefore ρ = member/ideal **conflates
  per-user renderer-permutation (`style_map`) recovery with latent decoding.**

### Ground 2 — baseline dominance on the pre-registered anchor cells (denominator-free; robust to Ground 1)
Interp pre-reg (N2/N3) restricts mechanism-strength anchoring to `camouflage_off` / `low_diversity`
/ `flat_theta`. In battery run 2 (void, diagnostic-only; raw metrics, which are denominator-free
and therefore immune to the ρ / style_map contamination):
- **`low_diversity`** (ideal 0.324): lookup control `nearest_neighbor` raw **0.162** BEATS the
  assigned should-win member `seq_window` raw **0.075** by **2.2×** (control ρ 0.447 vs member ρ 0.150).
- **`flat_theta`**: members at chance (`discounted_LS` 0.034, `running_average` 0.032).
- **`camouflage_off`** (threshold 0.8): best member `gbt` ρ 0.79 — still FAIL.
- Every assigned mechanism member FAILS its cell. The only cert "pass," `rag`/`stable_facts`
  (ρ 0.751), is N3-flagged instrument-fragile; constant cells (ρ 1.0) are N2-degenerate.

## hypothesis (closed)
"S3d v0's ρ isolates a latent-mechanism decoding capability." **Falsified:** ρ is style_map-dominated
at the ceiling, and the surviving in-cell headroom is captured better by a lookup baseline than by the
assigned mechanism member.

## baseline / ablation (evidence already produced — not re-run here)
- In-battery control baselines: `nearest_neighbor`, `count_table`, `transition_table`,
  `successor_map`, `fsm_planner`, `episodic_traversal`, `majority`, `global_prior`, `predict_all/none`.
- Decisive comparison: `nearest_neighbor` (lookup) > `seq_window` (mechanism) in `low_diversity`,
  raw metric (denominator-free).
- Ablations: 001A wrong-style_map + history-scramble + posterior-independence; 002A wrong-style_map
  on real cells.

## trace / replay
Evidence committed with this closure: `result.json`, `failure_manifest.json`,
`baseline_comparison.json`, `s3d_certificate_report.json`, `s3d_null_env_report.json`, `trace.jsonl`
(+ preserved `*_void*` variants). Diagnostics: `s3d_null_ideal_diag_001a/` (`30caa7f`),
`s3d_null_ideal_diag_002a/` (`5cb90397`). Machine-readable closure record:
`artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_v0_closure_record.json` (all numbers re-derived from the
committed artifacts, not hardcoded).

## acceptance gate (for THIS closure)
- `s3d_v0_closure_record.json` re-derives every cited number from committed artifacts and they match
  this card.
- Re-confirmed from the committed `baseline_comparison.json`: (a) no assigned mechanism member passes
  a discriminative cell; (b) `nearest_neighbor` raw metric > `seq_window` raw metric in `low_diversity`.
- Re-confirmed from committed `s3d_null_env_report.json`: ideal NULL metric > null limit.
- No banked artifact altered; no src/spec change; void evidence preserved (not patched).

## claim ceiling
Bounded closure evidence only. Establishes that S3d v0 **as an instrument** (i) cannot fairly isolate
latent signal from per-user `style_map`, and (ii) shows no mechanism>baseline separation on its own
pre-registered anchor cells. Does **NOT** prove: mechanism absence; falsity of any theory
(Bio-CMBC / CVPSM / VCCO / CMBC / R-G); absence of learning/adaptation; or that no future testbed
could find signal. **Tombstones the v0 instrument, not the research route.**

## reopen conditions (R2 successor — pre-registered)
A successor `S3d-R2` may reopen ONLY if, BEFORE any positive number exists, it pre-registers and then
demonstrates:
1. **Style-invariant / equal-access design:** either score in a permutation-invariant latent space,
   OR give the ideal the same information set as members (infer `style_map` from the eval-prefix; no
   handed `style_map`) — used consistently in BOTH the NULL guard AND the ρ denominator (no schema
   fragmentation / no second ideal).
2. **Mandatory falsifier:** the assigned mechanism member must **beat** (not tie) the
   lookup / nearest-neighbor / graph-cache / count-table / successor-map family on the discriminative
   cells by a pre-registered margin, with the full control family reported alongside.
3. **NULL clean** for the equal-access ideal.
If R2 cannot state ex ante *why* style-invariant scoring would separate the mechanism from the lookup
family, do not open it.

## stop condition
Terminal for S3d v0. No further v0 guard/threshold/env patching. Reopening v0 (as opposed to a fresh
R2 successor) is out of scope.

## rollback
Closure = documentation + a machine-readable record; it changes no science code and no banked
experiment artifact. Rollback = revert the closure commit. Void evidence and all prior banked
artifacts remain untouched.

## forbidden
Rewriting/patching void artifacts to pass; modifying src / spec / frozen_design; auto-reopening v0;
making any mechanism or theory claim from the void numbers.

## §operator acceptance (signature waived — solo project, 2026-07-05)
Per solo-efficiency policy, no per-card operator signature is required to bank this void/negative closure. Recorded as operator policy:
- [x] `S3D_V0_TOMBSTONED` and the two grounds accepted.
- [x] Pre-registered R2 reopen conditions accepted and binding.
Operator: Zhouyu (policy, unsigned)  Date: 2026-07-05
