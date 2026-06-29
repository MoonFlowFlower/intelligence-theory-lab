# Independent Audit — TLGP-001B-R2 Official Full Run

**Audit target:** `TLGP-001B-R2-FULL-ORCHESTRATION-AND-RUN-001`
**Final verdict:** `requires_official_bundle_repair_before_accepting_verdict`
**Scientific verdict under audit:** `tlgp001b_r2_invalid_learnability_floor_failed` — **sound and clean-room reproducible**, but the bundle is **not source-hash clean** and the working tree carries post-run forbidden-file drift.

## One-paragraph summary

The science is right. The reported INVALID-learnability-floor verdict is prereg-faithful, replay-valid, and correctly implemented: prereg canonical sha matches exactly; `compute_verdict` is pure with the frozen 7-terminal precedence (branch 2 fires on `not any(rung0)`, ahead of H0/H1/inconclusive, no `else→H0`); rung 0 fails 0/10 for both primary families because they memorize train (GRU ~0.97) but collapse on in-distribution held-out episodes of the same 8 rules (~0.45–0.55 ≪ floor 0.9), a failure that holds under *any* reading of the floor definition; and a clean-room replay (no repo imports) over all 830,000 trace rows reproduces every metric (max Δ 3.9e-15) and the exact verdict. What blocks a clean accept is provenance: on-disk `harness.py` (`8bd467d4`) ≠ the executed, thrice-pinned `6b32e47e`; the `delivered_equals_executed` gate is a tautology (`source_hashes()==source_hashes()`) that reported true while the file diverged; and `AGENTS.md` (a forbidden governance file) carries real post-run content drift that would now fail the run's own preflight. None of this touches the immutable, replay-verified artifacts — the repair is provenance-only, no re-run.

## What is solid (banked-as-evidence-quality)

- Prereg canonical sha `6e61a831…` matches; all frozen fields (DELTA 0.1, FLOOR 0.2, N_SEEDS 10, close ≥9/10, LCB mean−2σ/√N, world constants, 625 rules, 500/125 split, R0=8, primary GRU+Transformer, diagnostic MLP) match implementation.
- Rung 0 pass-rule (both 0a train AND 0b heldout ≥ ideal−DELTA on ≥9/10) is **prereg-mandated, not implementer-stricter**; ideal=1.0 is computed via the 001A Bayesian observer, not literal.
- Clean-room replay: 830,000 rows, trace sha matches, 0 per-row balanced-accuracy mismatches, all 766 metric means reproduced, independent precedence → `invalid_learnability_floor_failed`. Tamper flips 1.0→0.0.
- Model inputs exclude `rule_id` and `query_e` (structural boundary in `build_tensors`); leakage detector valid + catches planted/renamed + no false-flag on all 4 datasets.
- Ablations real/computed (context→~0.2 chance collapse; shuffle headroom ~0); scanner `cheap_baseline_saturation=false` computed; all split assertions true (disjoint, R0⊂train, 500/125).
- CUDA real: `cuda:0` probes read actual `model.parameters().device` and tensor `.device`; RTX 5070 Ti, torch 2.9.1+cu128; 16.03 h; predictions serialized to CPU ints; no CPU fallback.
- Git: HEAD unchanged `c142443e…`, branch correct, index empty, no add/commit/push/tag; forbidden **artifact** paths show 0 diff. Only one `result.json` (no duplicate/overwrite).

## Blockers (repair before banking)

- **B1 — harness.py provenance:** on-disk `8bd467d4` ≠ executed `6b32e47e` (pinned across smoke / preflight / end). Non-orchestrating CLI shim; verdict reproducible without it, but the prereg contract requires `delivered_sha256==executed_sha256` for *every* R2 src file. → Restore the executed harness.py or document+re-hash; verify on-disk==executed for all 9 files.
- **B2 — tautological provenance gate:** `delivered_equals_executed = source_hashes()==source_hashes()` cannot detect on-disk drift; it reported `true` while harness.py diverged. → Compare `source_hashes_at_preflight` (already captured) vs end-of-run hashes; fail-closed on drift.
- **B3 — AGENTS.md forbidden-file drift:** real post-run content change (~+37 lines, LF-normalized ≠ HEAD), re-introduced after the scope-cleanup revert; the working tree would now fail the run's own forbidden-diff preflight. → Revert AGENTS.md to HEAD.

## Non-blocking

- **N1** SHA256SUMS RUN_LOG.txt mismatch (final completion line appended after checksum — benign).
- **N2** Tree-wide CRLF drift on 2,760 tracked files (LF-normalized-equal to HEAD; cosmetic).
- **N3** Smoke manifest truncates on bash read in the audit sandbox (FUSE artifact; non-evidential file).
- **N4** Adjudication is witness-config-only (prereg-consistent saturation witness; full 14-config grid is trained/traced but only the witness gates).

## Banking

- **Do not bank yet.** After B1–B3 repair, bank only as: *“TLGP-001B-R2 official full run produced bounded INVALID due to learnability-floor failure under frozen prereg sha 6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7.”*
- **Do not** bank as H0, H1, 001A-downgraded, “within-episode headroom survives capable meta,” meta-learner failure in general, theory failure, mechanism evidence, or EGO progress.

## What this audit does not prove / next step

Bounded result-audit only. It does not prove the family cannot learn with more data/diversity, does not adjudicate 001A, does not establish H0/H1, and does not authorize 001C. **Next minimal action:** operator performs the bounded provenance repair (B1–B3), re-emits `source_manifest.json` + `SHA256SUMS.txt`, then re-presents for a short re-audit. No re-run, budget/grid/seed/prereg change, or route advancement is authorized by this audit.
