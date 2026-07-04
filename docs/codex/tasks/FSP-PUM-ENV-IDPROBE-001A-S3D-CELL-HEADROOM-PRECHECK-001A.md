# FSP-PUM-ENV-IDPROBE-001A — S3d Cell-Headroom Pre-check 001A

Status: **AUTHORIZED bounded diagnostic** (cheap, pre-battery). Estimates, for every should-win
cell, whether the exact ideal satisfies the spec's pre-registered cell-validity guard
(`ideal_cell − chance_cell ≥ 0.10`, spec §2 lines 43–44) using the SAME per-cell ideal + metric the
battery/cert uses — so we learn which cells would trip `s3d_cell_headroom_defect` BEFORE spending the
full battery (which STOPs the whole S3d on any defective cell). Does NOT run the full battery, does
NOT change the spec / guard / thresholds / strength / cert cells / filter.

## task id
`FSP-PUM-ENV-IDPROBE-001A-S3D-CELL-HEADROOM-PRECHECK-001A`

## why
The stable-fact diagnostic gave `stable_facts` recommend-conditional `ideal − chance ≈ 0.027 ≪ 0.10`
→ the rag cell is (pre-registered) defective by the spec's own guard. The repair report's 1-user
OVERALL metrics are unreliable for other cells (e.g. `constant_none` ideal ≈ chance, an artifact of
macro-balanced-accuracy over absent classes and/or an ideal that doesn't model the constant cell).
So the per-cell headroom must be measured with the correct metric before deciding.

## method (faithful + cheap)
- **Reuse the banked battery runner's per-cell ideal scoring** (`s3d_battery_runner_line30.py`
  `_score_ideal_cell` / its cert metric) — do NOT reinvent the metric or the ideal. Run **only the
  ideal** (not the members) on each should-win cell.
- Users: **k = 15** pre-registered eval users per cell (deterministic fractional-index selection over
  the cell's eval-user list, ascending; non-heldout; record resolved ids). Heldout 800–999 forbidden.
- Cells: every should-win cell in the frozen cert table — `degenerate_should_win_constant_none`,
  `degenerate_should_win_constant_saturated`, `camouflage_off`,
  `graph_cache_should_win_low_diversity_templates`, `rag_should_win_stable_facts`, `flat_theta`
  (NULL_env excluded — it is the null control, not a should-win cell). Use each cell's cert metric
  (e.g. recommend-conditional for `rag_should_win_stable_facts`), pooled over the k users.
- Per cell report: `ideal_metric`, `chance_cell`, `headroom = ideal − chance`, and the guard result
  vs `0.10`.

## interpretation guard (mandatory — do not mislabel)
For any cell where `ideal ≈ chance`, you MUST diagnose which of these it is before calling it a
defect:
- **CELL_DEFECTIVE**: the ideal correctly models the cell (argmax predictions track the cell's
  generative mode / channel) yet headroom < 0.10 → real pre-registered `s3d_cell_headroom_defect`
  candidate → successor spec.
- **IDEAL_MISSPEC**: the ideal does NOT model the cell (e.g. on a constant cell the ideal's argmax is
  not the constant symbol) → a filter coverage gap, NOT a cell defect → report separately.
- **METRIC_ARTIFACT**: the metric is degenerate for the cell (e.g. macro-balanced-accuracy over 32
  classes when the target has one class) → the guard is being applied on the wrong scale → report
  separately; do NOT declare the cell defective.
Evidence to include: for each such cell, the ideal's argmax-vs-generative-mode agreement on a few
turns, and the number of distinct target classes.

## decision (report; do not act on the battery)
Per cell: `CELL_VALID` (headroom ≥ 0.10) / `CELL_DEFECTIVE` / `IDEAL_MISSPEC` / `METRIC_ARTIFACT`.
Overall: list the cells that would block a full battery and why.

## claim ceiling
Cell-headroom pre-check only; a multi-user ESTIMATE of the spec's cell-validity guard, not the formal
160-user cert-set adjudication. No S3d certificate, NULL, environment-validity, gap, mechanism,
learning, agency, or EGO claim.

## stop condition
STOP + failure_manifest if any heldout user is touched, a spec/guard/threshold/strength change would
be needed, or the banked runner's ideal path cannot be reused faithfully (report rather than
reimplement silently). Preserve failures; do not patch; do not tune anything to pass.

## artifacts (under artifacts/FSP-PUM-ENV-IDPROBE-001A/)
`s3d_cell_headroom_precheck.json` (per-cell ideal_metric / chance / headroom / guard result /
verdict / argmax-vs-mode evidence; resolved user ids; reused runner sha256; single_thread_env), a
trace, `failure_manifest.json` if anything fails, `claim_ceiling`.

## rollback / dev rules
Read-only w.r.t. filter/spec/guard; isolated new diagnostic script reusing the banked runner; Codex
runs no git; emit an operator bank-ops proposal (HEAD-pin + reset + allowlist + staged-count +
zero-deletion + per-file Get-FileHash + scoped `git commit -- paths` + no push) and STOP for Claude
audit. Forbidden: heldout; changing spec / guard 0.10 / ρ thresholds / strength 3.2 / cert cells /
filter; tuning to pass; git; patching.
