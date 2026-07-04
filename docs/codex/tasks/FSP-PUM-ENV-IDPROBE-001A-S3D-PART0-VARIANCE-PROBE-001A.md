# FSP-PUM-ENV-IDPROBE-001A — S3d PART 0 Variance Probe 001A

Status: **AUTHORIZED for Codex implementation on operator hand-off.** Bounded measurement
addendum. Does **not** enter the certificate battery, does **not** change any frozen spec /
threshold / cert cell / NULL MDE / the 12.0 CPU-h line, does **not** run git.

## task id
`FSP-PUM-ENV-IDPROBE-001A-S3D-PART0-VARIANCE-PROBE-001A`

## problem definition
The banked S3d PART 0 STOP (projected 19.248 CPU-h > 12.0 line,
`s3d_compute_projection.json` sha256 `413ac0c7…`) rests on a **single** eval user (id 640)
extrapolated linearly: 17.7 of 19.25 CPU-h come from one user scaled ×1120 (ideal) and ×160
(prefix score), with no per-user variance. The operator's budget decision (BUDGET-DECISION-001A:
maintain STOP vs raise line) needs a bounded estimate of that projection's per-user spread to
(a) know how trustworthy 19.25 is, (b) size a new line if raising, and (c) detect the case where
the true projection is actually < 12 (STOP would then be a single-sample artifact).

## current stage
S3d PART 0 projection **refinement**, post-STOP / pre-budget-decision. Not the battery.

## hypothesis
Per-eval-user cost for the three dominant terms — ideal one-cell (camouflage_off),
`discounted_LS_lambda_0.95` score, `nearest_neighbor_user_matching` score — has bounded spread
such that a mean-based revised projection lies in a stated band around 19.25, and user 640 is not
a gross outlier. (Falsifier: band lower bound < 12.0 ⇒ STOP was single-sample; or spread so wide
the projection is uninformative ⇒ report as such.)

## baseline / ablation
**N/A by design.** This is a timing-measurement addendum, not a mechanism claim; no science
baseline or ablation is required or permitted to be read as evidence. Claim ceiling = projection
refinement only (see below). State this explicitly in `result.json` so no reviewer expects them.

## pre-registered sampling (anti-cherry-pick — fix BEFORE measuring)
- Measure **k = 5** eval users per term, chosen deterministically from that term's cell eval-user
  id list sorted ascending, at fractional indices {0.0, 0.25, 0.5, 0.75, 1.0} (first, q1, median,
  q3, last). Record the resolved ids in the artifact.
- User 640 is measured as a **fixed reference** and reported separately (it may or may not fall in
  the k=5; do not drop or swap users after seeing timings).
- Heldout users 800–999 **must not be touched**; assert `heldout_users_800_999_touched=false`.
- The one-time family `fit` (users 0–639) is measured **once** per family and reused for all users
  (the projection already treats fit as one-time). Do not re-fit per user.

## measurement (mirror the PART 0 runner exactly)
At threads=1 (OMP/MKL/OpenBLAS/NumExpr/torch = 1, torch device cpu), same specs/cells as
`s3d_part0_projection_runner.py`:
- ideal `FactoredExactFilter` one-cell per-user wall on `camouflage_off`;
- `discounted_LS_lambda_0.95` `score_one_user` wall on `flat_theta`;
- `nearest_neighbor_user_matching` `score_one_user` wall on `stable_facts`.
Revised per-term projection = `fit + mean_score × 160` (prefix families), `mean_per_user × 1120`
(ideal). Report per-term and total: mean, std, min, max, and a **revised total projection with a
min–max band**; state whether the band crosses 12.0.

## trace / replay requirement
Emit `trace.csv` (or `.jsonl`) rows: `user_id, term, wall_seconds, thread_env`. Record the
deterministic selection rule, resolved user ids, `single_thread_environment`, `code_path_hash`,
run started/finished, run wall-clock. Replay = same recorded user ids + single-thread reproduces
the measurement **structure** (absolute timings are machine-dependent; the selection and method
must replay exactly).

## acceptance gate (instrument — not a science pass/fail)
`s3d_part0_variance_probe.json` exists with: k=5 users by the pre-registered rule, per-term
mean/std/min/max, revised projection + band, `heldout_users_800_999_touched=false`,
single-thread accounting, `code_path_hash`, claim-ceiling field; AND no frozen
spec/threshold/cert-cell/NULL-MDE/12-line change; AND `s3d_certificate_report.json` /
`s3d_null_env_report.json` still absent (assert).

## claim ceiling
PART 0 compute-projection **refinement / per-user timing variance evidence only**. No certificate,
NULL, environment-validity, baseline-power, headroom, gap, mechanism, learning, agency, or EGO
claim. Does **not** overturn or strengthen the banked STOP; it only bounds the projection's
uncertainty for the operator's budget decision.

## stop condition
STOP + `failure_manifest.json` if: any heldout user is touched; any timing or revised projection
is non-finite; the probe would require changing any frozen spec/threshold/cell/line; or the run
would exceed 12.0 CPU-h (it will not; guard anyway). Do **not** tune user selection after seeing
timings.

## rollback plan
Probe writes only new artifacts under `artifacts/FSP-PUM-ENV-IDPROBE-001A/`
(`s3d_part0_variance_probe.json`, its trace, optional `failure_manifest.json`) plus an isolated
new script `artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_part0_variance_probe_runner.py` and a proposed
successor BANK-OPS file. Touches no existing artifact and no `src/` logic. Rollback = delete the
new probe artifacts; nothing else affected. Codex runs no git.

## dev rules / forbidden
Isolated new script reusing existing measurement functions; do **not** modify
`s3d_part0_projection_runner.py` or any frozen file; do **not** run git; emit a proposed
operator bank-ops script and STOP for Claude audit. Forbidden: touching heldout 800–999; changing
the 12 line / thresholds / cert cells / NULL MDE / any spec; starting the certificate battery or
NULL-env; git commit/push; modifying existing artifacts; any heldout/label leakage.
