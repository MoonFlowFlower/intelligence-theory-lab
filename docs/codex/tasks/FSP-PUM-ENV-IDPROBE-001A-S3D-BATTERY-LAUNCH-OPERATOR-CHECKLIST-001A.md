# FSP-PUM-ENV-IDPROBE-001A — S3d Battery Launch: Operator Checklist 001A

Thin orchestration layer over the already-signed `S3D-BATTERY-EXEC-001A` (execution mechanics live
there; do not restate/alter them). Roles: **Codex executes** (no git), **Claude audits**,
**operator banks**. HEAD at authorization: `2a4502a`.

Prerequisites cleared this session: `c0c6bf4` (001B-IMPL) audit = ACCEPT; 22.297 CPU-h variance
check = robust < L=30 (contention-robust CPU gate + CPU-based runtime guard).

## Step 0 — Go/No-Go pre-flight (read-only; the runner re-verifies all of these and hard-STOPs if any fail)
- [ ] HEAD = `2a4502a` (or a descendant that did not touch the frozen spec / exec card / budget note).
- [ ] `S3D-BUDGET-DECISION-001A` §8 signed: `[x] B`, `New line = 30.0`, operator, date, and banked.
- [ ] `S3D-SHOULD-WIN-NULL-ENV-SPEC-001B` §7 signed: `[x] 2a k=5`, both firewalls `[x]`, operator, date, banked.
- [ ] `s3d_001b_impl_report.json` and `s3d_part0_variance_probe.json` banked at HEAD; STOP commit `17cce05` in ancestry.
Note: Step 0 is a human sanity check. `s3d_battery_runner_line30.py::_verify_preconditions` enforces
all of it and writes a precondition failure manifest + STOP if anything is missing — launching without
a signature cannot silently proceed.

## Step 1 — Bank the interpretation pre-registration FIRST (before any battery work)
- [ ] Fill + bank `S3D-BATTERY-INTERPRETATION-PREREG-001A` (N1/N2/N3). Scoped commit, no push.
This must predate the run so N2 (constant cells = degenerate controls) and N3 (stable_facts fragile)
are pre-registered, not post-hoc. **If skipped, a "green" battery can leak the claim ceiling.**

## Step 2 — Hand Codex the execution instruction (separate message) and let it run
- [ ] Codex runs the committed `s3d_battery_runner_line30.py` entry point at HEAD. No git. No temp
      report driver (N1). Reads L=30 from the signed budget note.
- The runner self-sequences: precondition → PART-0 re-gate under L=30 (writes
  `s3d_compute_projection_line30.0.json`) → preflight guards (BASE-invariance / cert-only) → parallel
  battery (N_workers×1thread ≤ physical cores; runtime CPU guard @30) → cert / NULL / baseline /
  ablation / replay / result → emits an operator bank-ops proposal.
- [ ] Codex STOPs for Claude audit after the run. **Codex does not bank.**

## Step 3 — What to expect / watch
- Expected on success: `result.json` verdict populated, `battery_launched: true`, all six evidence
  artifacts present, `applied_cpu_hour_limit = 30.0`, contention-robust CPU-h reported (≈22–25 h
  expected) with wall-disclosed alongside, parallel==serial bit-identical asserted on ≥1 unit.
- Legitimate STOPs (preserve, do NOT patch, return to Claude): precondition unmet; PART-0 re-gate
  > 30; runtime CPU guard > 30 (a **2nd** breach returns to operator — no auto-raise); any heldout
  user 800–999 touched; BASE-invariance regression fail; `FAIL_NULL_FALSE_HEADROOM` (all S3d
  results void — keep them void). A STOP is a real outcome, not a failure of the launch.

## Step 4 — Claude audits the battery result
- [ ] Against the frozen spec **and** the `INTERPRETATION-PREREG-001A` card (N1 provenance/replay;
      N2 constant = control-only; N3 stable_facts = fragile; strength anchored on
      camouflage_off / low_diversity / flat_theta).
- Output: verdict + blocking / non-blocking / required fixes / may-bank.

## Step 5 — Operator banks (only after Claude ACCEPT)
- [ ] Run the runner-emitted operator bank-ops (HEAD-pin + `git reset` first + allowlist +
      staged-count + zero-deletion + per-file `Get-FileHash` + scoped `git commit -- paths` + **no push**).
- Per `git-sandbox-constraints`: do `git reset` unconditionally before staging to avoid a poisoned
  index; verify provenance host-side (not via the FUSE mount).
- If Claude returns blocking issues → fix/STOP, do not bank.

## Stop-loss / rollback
Line change and all battery artifacts are isolated new files; nothing banked is overwritten.
Rollback = discard the new battery artifacts (banked spec / STOP / probe untouched). No auto-retry,
no auto-raise of L.

## Claim ceiling
This checklist authorizes execution + banking of bounded S3d instrument evidence at L=30 only. It
proves nothing about mechanism, learning, agency, or theory correctness.
