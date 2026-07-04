# FSP-PUM-ENV-IDPROBE-001A — S3C-BATTERY-SPEC-001C (operator budget decision)

Status: DRAFT until operator banks this file; the checkpoint-commit act is the
operator's signature on this decision.
Decision owner: operator (Zhouyu), 2026-07-03. Drafted by Claude (lab auditor role)
at operator instruction after selecting fork option A.

## Decision

The S3c battery-fitting compute budget line is raised ONCE, for S3c only:
24.0 CPU-h → 30.0 CPU-h.

Trigger: S3c-R2 PART 0 v2 measured projection = 24.256926 CPU-h (overshoot 1.07%),
STOP per 001B Amendment 4 (s3c_compute_projection_v2.json sha256 e0e3fb22…;
failure manifest v2 55c82caf… preserved).

## Why this is an operator budget decision, not threshold tuning

1. Line origin: the 24 CPU-h S3c number was transplanted by the auditor in 001A from
   the S2 precedent as a budget convention; it was never derived from a resource
   constraint and no claim attaches to it (no "tractable" verdict is emitted for
   battery fitting).
2. Basis quality: the v2 projection is measured per cost class (six one-set
   measurements, single-thread), not heuristic; the overshoot is 1.07%.
3. Challenger strength is untouched: grids (24 decoder + 16 seq configs), members,
   GBT data budget, validation split, metric, and selection rule are all unchanged.
   The alternative (weakening the challenger family to fit an arbitrary budget) was
   rejected as epistemically backwards: baseline power is evidential, the budget
   number is not.
4. Score exposure at decision time (full disclosure): the only S3c numbers in
   existence are chance-level cheapest-config internal-validation figures
   (0.0299, 0.0299, 0.0331, 0.0311, 0.0317, 0.0317 vs chance 0.03125) and one R1
   figure (0.0299). Nothing selectable, nothing heldout, nothing gap-shaped. This
   decision cannot be tuned toward results because no results exist.

## Firewall — precedent protection

The S2/S2e 24 CPU-h TRACTABILITY line (S5-projection, claim-bearing, pre-registered in
S2b and held through two honest failures) is a DIFFERENT object. It remains in force,
unchanged. This 001C decision must never be cited as precedent for moving any
claim-bearing threshold or evidence gate. Budget lines and evidence thresholds are
distinct categories; only the former is operator-adjustable, and only with a signed
decision note like this one.

## Runtime guard

- During the sweep, cumulative measured CPU-h is tracked per completed config; if the
  cumulative total exceeds 30.0 CPU-h, STOP immediately with a failure manifest.
  A second breach is NOT operator-pre-authorized; it returns to the operator.
- Config-level parallelism is permitted: each config runs as a threads=1 process
  (OMP/MKL/torch num_threads=1); CPU-h = sum over configs of per-config wall-clock at
  threads=1. Wall-clock may therefore be shorter than CPU-h; the accounting fields
  must report both.

## Everything else

001A as amended by 001B remains fully in force: grids, selection rule, split, heldout
prohibition, F2 thresholded vocabulary (reuse the persisted
s3c_models/f2_ngram_vocabulary.json, sha256 3a08b3b5…, verified before use), GBT
half-data budget, teacher-forced training, incremental features, GPU prohibition,
artifacts list, claim ceiling.
