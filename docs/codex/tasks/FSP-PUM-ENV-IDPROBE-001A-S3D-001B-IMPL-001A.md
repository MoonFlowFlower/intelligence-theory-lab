# FSP-PUM-ENV-IDPROBE-001A — S3d 001B Implementation 001A

Status: **AUTHORIZED on 001B being signed+banked.** Implements the three deltas of the signed
`S3D-SHOULD-WIN-NULL-ENV-SPEC-001B` (leo; guard 2a k=5). Bounded, isolated. Does NOT run the full
battery (separate step). Does NOT change any 001A invariant (§4 of 001B): 18 members, member ρ
thresholds 0.50/0.80/0.90, the 2 cert-only variants, BASE-invariance, NULL MDE `chance+0.005`,
`strength=3.2`, cert cells, trace/replay, claim ceiling.

## task id
`FSP-PUM-ENV-IDPROBE-001A-S3D-001B-IMPL-001A`

## precondition (BLOCKING)
`FSP-PUM-ENV-IDPROBE-001A-S3D-SHOULD-WIN-NULL-ENV-SPEC-001B.md` §7 signed (`[x] 2a k=5`, both
firewalls `[x]`, operator+date) AND banked. If unmet → write precondition failure manifest, STOP.
Read L from the signed budget note (still L=30).

## DELTA 1 — constant-cell ideal (src/fsp_pum_env/factored_filter.py)
Implement the exact ideal for `degenerate_should_win_constant_none` and
`degenerate_should_win_constant_saturated`, mirroring the generator
(`simulator._constant_cert_distribution` → constant symbol 0 / 31, through the per-user style map).
Add the dispatch + table; leave every other branch byte-identical. **Not** a hard-coded "return
symbol 0" lookup — derive from the constant generative distribution + style map (so it would track a
different constant if the generator changed); the audit will reject a label-leaking constant.

## DELTA 2 — recalibrated cell-validity guard (in the banked cert runner's guard check)
Replace `ideal_cell − chance ≥ 0.10` with the signed **2a**: `ideal_cell − chance ≥ k × SE_cell`,
`k = 5`. `SE_cell` = binomial SE of the cell metric at that cell's eval-point count
(`sqrt(chance*(1-chance)/n_cell)`), computed from the actual eval-point count per cell/scope. Single
isolated change to the guard check; no second logic path. Emit per-cell `n_cell`, `SE_cell`,
`k*SE_cell`, `ideal−chance`, pass/fail. The guard is computed on the **ideal only**, before any
member result is scored (firewall).

## DELTA 3 — canonical metric pinned + reconciled
Declare the banked cert runner's scorer canonical for every cell metric (incl. recommend-turn-
conditional). Add a one-shot verification that it computes recommend-conditional correctly on a fixed
fixture, and record WHY the old inline diagnostic scorer produced `0.0586` vs the canonical `0.1363`
(e.g. per-user-avg vs pooled, or recommend-turn identification). No adjudication may use the old
scorer.

## gates (all BLOCKING)
1. **Regression**: re-run the ideal on every already-supported variant (base/camouflage_off,
   constant_none, constant_saturated, low_diversity, NULL_env, probe_channel_off, flat_theta,
   stable_facts) — result bit-identical to the pre-change snapshot for the variants NOT being fixed;
   `camouflage_off` ideal metric `0.09948462995337995` exact. Constant cells change (that's the fix)
   — but no OTHER variant's ideal may change.
2. **Ideal-sanity (canonical metric, per cell)**: on EVERY should-win cell, ideal ≥ every member on
   that cell's canonical metric (including recommend-conditional for rag). Report the table.
3. **Recalibrated guard**: apply Delta-2 guard to every should-win cell; report pass/fail per cell.
   (Expectation from the pre-check + Delta-1 fix: all cells pass under k=5; if any cell still fails,
   STOP and report — do NOT adjust k or strength.)
4. **Constant-cell oracle/anti-leak**: confirm the constant-cell ideal derives from the generative
   distribution + style map, not a hard-coded symbol/label lookup.
5. `py_compile` + focused `pytest` pass; banked 001A/STOP/probe/repair/pre-check artifacts
   byte-unchanged.

## claim ceiling
Implements 001B; enables S3d execution under the corrected instrument. No S3d certificate, NULL,
gap, mechanism, learning, agency, or EGO claim. Actual S3d evidence comes from the battery re-run.

## stop condition
STOP + failure_manifest if: precondition unmet; any non-fixed variant's ideal changes; a member ≥
ideal on any cell's canonical metric; any cell still fails the k=5 guard (report — do NOT tune k or
strength); the constant-cell ideal would need a label-leaking lookup; a frozen 001B-invariant change
would be required. Preserve failures; do not patch.

## rollback / dev rules
Isolated changes to `factored_filter.py` (constant-cell table) + the guard-check + canonical-scorer
pin. Revert = restore prior branches/guard. No banked artifact modified. Codex runs no git; emit an
operator bank-ops proposal (HEAD-pin + reset + allowlist + staged-count + zero-deletion + per-file
Get-FileHash + scoped `git commit -- paths` + no push) and STOP for Claude audit. Forbidden: changing
`strength=3.2` / ρ thresholds / member set / NULL MDE / other 001B invariants; tuning k or strength to
pass; label-leaking constant lookup; second logic path; git; using the non-canonical scorer.

## artifacts (under artifacts/FSP-PUM-ENV-IDPROBE-001A/)
`s3d_001b_impl_report.json` (per-cell ideal metric / SE_cell / k*SE / guard result; regression table;
ideal-sanity table on canonical metric; scorer reconciliation; code_path_hash; single_thread_env),
trace, `failure_manifest.json` if anything fails, `claim_ceiling`.
