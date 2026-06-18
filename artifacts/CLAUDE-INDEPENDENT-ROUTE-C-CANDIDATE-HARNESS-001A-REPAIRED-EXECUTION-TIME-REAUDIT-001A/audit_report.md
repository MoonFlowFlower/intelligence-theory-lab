# Independent Hostile Execution-Time RE-AUDIT — Route C Candidate Harness 001A (Repaired Bundle)

**Audit ID:** CLAUDE-INDEPENDENT-ROUTE-C-CANDIDATE-HARNESS-001A-REPAIRED-EXECUTION-TIME-REAUDIT-001A
**Date:** 2026-06-16
**Branch / HEAD:** `codex/meta-theory-scaffold` / `b45598b1c56080f2f850ae088f42cf585950483e`
**Role:** ITL Same-Agent Bridge Audit Role 001 (independent red-team, read-only)

## Verdict

**`requires_harness_repair_before_negative_evidence_admission`**

Admission **not** granted. One blocker remains (B4). It is narrow and trivially repairable; the underlying negative signal is sound and reproduced.

## Core question (from the task card)

> Does the repaired harness now make `close_or_downgrade` a computed, fail-able verdict derived from real gates, rather than a hardcoded or self-reported outcome?

**Yes for the verdict itself (B1).** Proven by execution: the exact repaired `derive_verdict_from_gates` flips `close_or_downgrade → candidate_margin_cleared` when the fair baseline is moved below the candidate across the equivalence band. This is the precise opposite of the prior audit, where the literal verdict stayed `close_or_downgrade` while the computed gates flipped.

**But the bundle still cannot be admitted as clean computed negative evidence**, because the source-pin truncation readback (check 9 / prior blocker B4) is non-fail-able as actually invoked, and the truncation failure mode it is supposed to catch is demonstrably live in this environment.

## Prior blockers — disposition

| Prior blocker | Status | Basis |
|---|---|---|
| **B1** result.json verdict/terminal_reason were non-computed literals | **FIXED** | `verdict = derive_verdict_from_gates(...)['verdict']` (runner.py:1679); derived terminal_reason/stop_conditions; assert before write (1753-4). Execution probe: verdict fail-able both directions. |
| **B2** access parity self-reported (static all-true, no traces) | **FIXED** | `compute_access_parity_report` compares 11 trace-derived dimensions; fail-able negative control (`access_parity_failed`); consumed by saturation gate + verdict derivation. |
| **B3** saturation control single-branch, didn't consume parity | **FIXED** | `build_saturation_failing_negative_control` runs both `close_or_downgrade` and `not_saturated` through the same callable and reads the parity report (verdict + file sha256). |
| **B4** source-pin hardcoded `prefix_truncation_detected=false` | **NOT SUBSTANTIVELY FIXED — BLOCKER** | De-hardcoded but inert as invoked (self-comparison; no independent reader; no truncated-prefix positive control). |

Also fixed since the prior audit: **N2 (leakage)** now scans the real produced artifacts and adds a clean-negative control.

## What is genuinely sound (independently reproduced)

Reproducing the deterministic generator + scorer from scratch (no harness import):

- candidate per-seed `[1.0, 1.0, 1.0, 1.0, 1.0]` → **1.0**
- `exhaustive_legal_query` per-seed `[1.0, 1.0, 1.0, 1.0, 1.0]` → **1.0**
- passive `positional_first_k` per-seed `[0.5, 0.5, 0.5, 0.0, 0.5]` → **0.4** (byte-exact match to committed `result.json`)
- **candidate − strongest-fair delta = 0.0**

The negative finding is overdetermined: the candidate is *code-identical* to `exhaustive_legal_query` (both call `query_all_policy` with `budget = item_count = 8 = all legal actions`), so both recover the hidden set exactly. All 12 fair baselines (including all 6 graph-cache challengers) tie at 1.0; the 8 passive baselines are genuinely discriminative (0.16–0.40). The scorer is real, not pinned to 1.0.

## The remaining blocker — B4 (check 9)

`read_file_pin` was made *capable* of detecting prefix truncation, but `build_source_pin_readback_report` calls it as `read_file_pin(path, repo_root)` — with **no** `expected_bytes` and **no** `shell_read_bytes`. Consequently:

- `expected = first` (the same, possibly-truncated read) → `authoritative_truncated = len(first) < len(first) = False`
- the shell branch is `None` → `prefix_truncation_detected` is **structurally always False**

`source_pin_readback_report.json` confirms `shell_mount_read_compared: false` and `prefix_truncation_detected: false` on all four pins, with `expected_size == observed_size`. The only forged-anchor positive control exercises **hash/reference/alias forgery**, not truncation, so **no truncated-prefix positive control exists**.

This is not hypothetical. The failure mode is **live in this very environment**:

- the Linux mount serves `runner.py` at **55976 bytes** (sha `a910704…`), missing `run_harness()`/`main()`, while the harness's own pin records the authoritative file at **72187 bytes** (sha `44b88044…`);
- `provenance_rows.jsonl` was likewise truncated mid-row-114 on the mount.

Execution probe (`/tmp/reaudit_b4.py`): even when the on-disk file *is* the 55976-byte truncated prefix, the as-invoked detector reports `prefix_truncation_detected = False, conflict_status = no_conflict`. The function only returns `True` when the caller passes `expected_bytes`/`shell_read_bytes` — which it never does. The `derive_verdict_from_gates` source-pin gate therefore can never fire.

Per the card's check-9 reject conditions, **#2 (no truncated-prefix positive control)** and **#4 (depends only on a known unreliable mounted path)** are both triggered.

## Why this blocks admission rather than being waived

The negative signal does not *depend* on the source-pin gate, and B4's failure cannot inflate the negative claim. But the card makes source-pin readback an explicit gating check, and its Acceptance Condition is conjunctive ("…replay, ablation, leakage, source-pin readback, and provenance are callable and not self-reported"). The source-pin truncation verdict is self-reported-absent. Admitting the bundle as *clean* computed evidence while its only source-integrity control provably cannot catch the environment's actual corruption mode would be exactly the non-fail-able-control pattern this lab forbids. The fix is mechanical, so this is repair-required, not unrepairable.

## Required fixes for admission

1. Give `read_file_pin` a real second signal in `build_source_pin_readback_report` (independent/shell cross-read, or trusted external expected size/hash), so truncation is compared against something other than the same read.
2. Add a **truncated-prefix positive control** that drives `prefix_truncation_detected=true` (and a conflicting `conflict_status`) through the real callable.
3. Make the `derive_verdict_from_gates` source-pin gate exercisable end-to-end (a forced conflict must drive `verdict → invalid`), demonstrated in-bundle.
4. *(Recommended, non-blocking)* Execute the replay sub-controls instead of asserting `fail_closed` literals; compute `verdict_consistency_check` by real comparison rather than a `True` literal.

## Non-blocking issues

- **N1** Replay sub-controls (`corrupted_state`/`missing_observation`/`forbidden_truth_field_read`) remain hardcoded `fail_closed` literals (main replay recomputation is genuine).
- **M1** `verdict_consistency_check.matches_recomputed_verdict` is a hardcoded `True`; the run-time assert is tautological. The real protection is the line-1679 assignment.
- **E1/E2** Live mount truncation prevented full in-sandbox end-to-end re-execution and recomputation of `code_path_hash`; source was verified via the authoritative file-API and fail-ability via direct execution of the exact repaired gate functions. *(This environment fact is what makes B4 material.)*

## Routing (observation, not authorization)

This Route C surface is trivially saturated because `query_budget == full legal action space`: any policy that queries every legal action recovers the hidden set. The correct routing is **close/downgrade this candidate surface**. **Do not repair the candidate to beat the baseline** — the only admissible repair is the B4 computed-evidence-path fix so the existing negative evidence can be admitted cleanly. A non-trivial surface would need `query_budget < full legal action space` (or otherwise block exhaustive legal query, graph-cache, lookup-imitation, and direct-optimizer from trivially recovering the hidden set).

## Claim ceiling

Execution-time hostile re-audit of a repaired bounded local Route C candidate harness evidence bundle only. No Route C mechanism validity, hidden-self-set inference, self-boundary evidence, candidate success, Gate pass, mainline/runtime/live effect, agency, autonomy, consciousness, emotion, stable user benefit, or EGO readiness.

## Scope compliance

No repo writes (probes in `/tmp` only; this audit output is my own dir). No source/test/target-artifact modification. No Gate run. No commit/push/tag/remote-anchor. The PAT in `.git/config` line 18 was not read or exposed.
