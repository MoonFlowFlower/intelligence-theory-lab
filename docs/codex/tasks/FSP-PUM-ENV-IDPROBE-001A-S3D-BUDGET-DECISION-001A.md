# FSP-PUM-ENV-IDPROBE-001A — S3d Budget Decision 001A

Status: **PROPOSAL — UNSIGNED. Not self-authorizing.** This note does **not** change the
pre-registered `12.0 CPU-h` S3d budget line, does not authorize any certificate / NULL-env
run, and does not shrink scope. Any change to the line takes effect only when the operator
signs Section 8 (spec §6: budget is "operator-adjustable only by signed decision note").

## 0. Base pin

- BASE_PIN: `80bfad4` / `80bfad4f061962ffa0ba120ea3e08b97cb93c2c1`
- Predecessor to bank first: the S3d PART 0 STOP boundary, commit message
  `FSP-PUM-ENV-IDPROBE-001A S3d PART0 projection STOP >12 CPU-h` (BANK-OPS 001A).
  This decision note is a **separate** artifact and is **not** part of that 6-file STOP bank.

## 1. Decision required

The pre-registered PART 0 compute-projection gate returned
`STOP_s3d_part0_projection_exceeds_12_cpu_hours` (projected 19.248 CPU-h > 12.0 line).
Per spec §6 the executor may not shrink grid/member/threshold to proceed. The open question
is an operator budget/value call: **do we spend the compute to run S3d SHOULD-WIN-NULL-ENV,
or maintain the STOP and record it as a bounded boundary result?**

## 2. Evidence base (and its limit)

- Projection artifact: `artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_compute_projection.json`
  (sha256 `413ac0c7…`), verdict corroborated by failure manifest `22a4519f…`.
- Arithmetic verified: 22 components sum to 19.24812 CPU-h; STOP correctly fired; the 12.0
  line and the `>12 = STOP, no executor shrinking` rule were pre-registered in the spec
  freeze commit `eea261d` (before the run) — no post-hoc threshold tuning.
- **Load-bearing caveat.** 17.7 of the 19.25 CPU-h come from **one** eval user (id 640)
  scaled linearly: ideal 7.88 (25.3 s × 1120 unit-cells), discounted_LS 5.63, NN 4.21
  (each `fit + 160 × score_one_user`). There is **no per-user variance estimate**. The
  non-ideal / non-heavy remainder is only ~1.5 CPU-h. Therefore `19.25` is a single-sample
  linear point estimate, not a tight cost: if user 640 is ~1.6× the eval-set mean the true
  figure could approach the line; it could equally be higher. The STOP is still valid (the
  linear-from-one-unit method and the `>12` rule were both pre-registered, and the claim
  ceiling is "projection exceeds line", not "the real run costs 19.25 h"). But the exact
  number must not be treated as ground truth when setting a new line.

## 3. Options

| Option | Who can authorize | Compute cost | What it buys | What it costs |
|---|---|---|---|---|
| **A. Maintain STOP** | operator (this note) | 0 | Clean, pre-registered boundary result; front moves to next queued item | S3d should-win / NULL-env instrument sanity stays **unexecuted** |
| **B. Raise the line, run** | operator (signed) | ~20–30 CPU-h (less wall with permitted process parallelism) | Actual S3d results: does should-win pass, and does NULL-env show metric ≤ chance+0.005 for every member (no false headroom) | Compute; residual risk of a second in-run breach if the line is set too tight |
| **C. Revise scope to fit <12** | operator (signed spec revision only) | <12 | Fits current line | **Dominated.** Fewer eval users inflates the binomial SE and weakens the NULL MDE 0.005 (which needs n≈48k = ~160 users × 300 turns); dropping cost classes removes the mandatory graph-cache / retrieval / LS challengers — i.e. it discards the exact baseline-immunity the certificate exists to provide |

Executor is forbidden to perform C (spec §6). C is listed only for completeness.

## 4. Cheapest de-risking step (recommended before B)

Before committing to a full battery, resolve the single-sample caveat directly: re-run the
existing PART 0 measurement path on **≥3 eval users** (e.g. ids 640, 720, 999-adjacent
non-heldout) instead of one, and report mean and spread of `projected_one_member_cell_seconds`
for the two dominant families plus the ideal term. Cost is a small multiple of the existing
PART-0 probe (minutes-to-≈1 h, well under the line). Output: a bounded estimate with a spread,
which tells you (a) whether 19.25 is trustworthy and (b) how much headroom a raised line needs.
This converts "raise the line by guesswork" into "raise the line to `ceil(1.3 × probed_mean)`,
floor 24 CPU-h." It also re-tests, cheaply, whether the true projection might actually sit
under 12 (in which case the STOP was a single-sample artifact and B becomes free).

## 5. Auditor recommendation (bounded)

- **If** any downstream FSP card will rely on the S3d certificate instrument to make an
  environment-validity / headroom / gap claim → the instrument's should-win + null sanity is
  on the critical path. Prefer **B**, but gated on §4 first, then set the line with margin and
  re-run the PART-0 projection under the new line before launch (the PART-0 gate still applies).
- **If** S3d is only a nice-to-have sanity and no queued card depends on the S3d instrument →
  prefer **A**: bank the STOP as bounded boundary evidence and advance the front.
- I do not have visibility into the downstream dependency graph; that determination is the
  operator's. This note deliberately stops at framing it.

## 6. Claim ceiling / firewall

- This note and any resulting run remain bounded to: compute-budget decision + (if B) S3d
  should-win / NULL-env instrument evidence under the pre-registered contract. **No**
  environment-validity, baseline-power, headroom, gap, mechanism, learning, agency, EGO, or
  readiness claim is implied.
- Spec §6 firewall carried forward: the S3d budget line is a convention, **not** claim-bearing,
  and must **never** be cited against the S2 tractability line (001C precedent).

## 7. What this note does NOT do

Does not change the 12.0 line; does not authorize a certificate or NULL-env run; does not
authorize push / tag / remote-anchor; does not shrink members / grid / thresholds; does not
claim any S3d result; is not part of the STOP bank commit.

## 8. Operator decision (sign to take effect)

**Auditor recommendation (post-probe, 2026-07-04):** Option **B**, **L = 30.0 CPU-h**. Rationale:
the variance probe confirms PART-0 costs ~17–19 CPU-h robustly > 12 (two independent full
estimates 17.09 & 19.25; band floor 15.97). The pre-probe formula floor is 24, but the probe
exposed cross-run timing noise up to ~2.4×/term, so 30 gives margin against a second in-run breach
and reuses the existing S3c-R3 30h runtime-guard precedent. To sign: check `[x] B`, write `30.0`
as the new line, fill Operator + Date below, then bank this note (`scripts/s3d_authorize_B_bank.ps1`).
L is yours to set; 24–30 is the defensible range.

```
Decision (choose one):
  [ ] A  Maintain STOP; record boundary; advance front.
  [X] B  Raise line to ______ CPU-h and authorize S3d run
         (recommended: run §4 variance probe first; then line = ceil(1.3 × probed_mean), floor 24).
  [ ] C  Authorize a signed spec revision id ____________ (scope change; power tradeoff acknowledged).

Preconditions for B/C: re-run PART-0 projection under the new line before launch; PART-0
gate and the runtime guard (STOP at line; second breach returns to operator) remain in force.

Operator: _________Leo_____________    Date: ____26/7/04______    New line (if B): __30___ CPU-h
```
