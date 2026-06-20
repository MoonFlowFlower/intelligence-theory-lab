# TLGP-001B-R2 Official Bundle Provenance Repair 001

Task id: `TLGP-001B-R2-OFFICIAL-BUNDLE-PROVENANCE-REPAIR-001`

Task verdict: `tlgp001b_r2_official_bundle_provenance_repaired__ready_for_short_reaudit`

## Scope

Operator scope: provenance-only, no scientific mutation.

Current layer: engineering implementation + mechanism-hypothesis preflight execution / provenance repair.

Mainline integration status: none. No EGO mainline, runtime, admission, bridge, product behavior, or agent capability integration is authorized.

Enabled status: isolated offline TLGP-001B-R2 official full-run bundle provenance repair only. No official rerun and no 001C advance.

Claim ceiling: provenance repair only. This task cannot prove TLGP-001B-R2, adjudicate TLGP-001A, authorize 001C, or prove learning-as-mechanism, agency, self, subjectivity, intelligence, autonomy, EGO readiness, runtime readiness, companion readiness, or mainline effect.

## B1 - harness.py Source-Hash Repair

- Executed/pinned `harness.py` SHA256: `6b32e47ef8bf9ad91716418ede7611ff011a0bdaa5a1c37ebc1b739c580c576f`
- Restored/current on-disk `harness.py` SHA256: `6b32e47ef8bf9ad91716418ede7611ff011a0bdaa5a1c37ebc1b739c580c576f`
- Equality result: `true`
- Restoration source: live workspace file already matched the official executed/pinned hash at repair time; no `harness.py` rewrite was required in this task.

## B2 - Repaired Current-vs-Executed Provenance Comparison

The original official `delivered_equals_executed` flag was tautological for post-run drift detection because it compared current source hashes against another current `source_hashes()` readback. This repair supersedes that flag with a fail-closed comparison between official executed/pinned source hashes and fresh current on-disk SHA256 values.

| R2 source file | Executed/pinned SHA256 | Current on-disk SHA256 | Equal |
| --- | --- | --- | --- |
| `src/tlgp_001b_r2/__init__.py` | `3c61963f7e387ea7f1dabc8ae31d725f8d29b57d525445d62bec017a748d183b` | `3c61963f7e387ea7f1dabc8ae31d725f8d29b57d525445d62bec017a748d183b` | `true` |
| `src/tlgp_001b_r2/harness.py` | `6b32e47ef8bf9ad91716418ede7611ff011a0bdaa5a1c37ebc1b739c580c576f` | `6b32e47ef8bf9ad91716418ede7611ff011a0bdaa5a1c37ebc1b739c580c576f` | `true` |
| `src/tlgp_001b_r2/lower_reference.py` | `cd701b2f4adcf9d8c66f28f0e797cdf748a7f4560c682953829b99eb85d28cf6` | `cd701b2f4adcf9d8c66f28f0e797cdf748a7f4560c682953829b99eb85d28cf6` | `true` |
| `src/tlgp_001b_r2/meta_learners.py` | `358d2bb2449f88ff5c73de52fcabcbba17f40b22dabc5c484f7b67da627e1b6f` | `358d2bb2449f88ff5c73de52fcabcbba17f40b22dabc5c484f7b67da627e1b6f` | `true` |
| `src/tlgp_001b_r2/official_full.py` | `1101ef25de3c60e30d1e42343d543dc6e3fd6d49aedfac1bf2e974a3f46ff6f3` | `1101ef25de3c60e30d1e42343d543dc6e3fd6d49aedfac1bf2e974a3f46ff6f3` | `true` |
| `src/tlgp_001b_r2/preregistration.py` | `6a5a0273e7c3b0c2cce031dcf2b495646d87ecea7630d725c84def8f9ce27480` | `6a5a0273e7c3b0c2cce031dcf2b495646d87ecea7630d725c84def8f9ce27480` | `true` |
| `src/tlgp_001b_r2/splits.py` | `ca2852a1ca69ba5277872bf5b0780163d0c79fbf0b5b2c7075bb740ef9981ad5` | `ca2852a1ca69ba5277872bf5b0780163d0c79fbf0b5b2c7075bb740ef9981ad5` | `true` |
| `src/tlgp_001b_r2/verdict.py` | `ac80b06083b24a43c5b3615ac0185acd1817554844ba1d145d1e380391ae2375` | `ac80b06083b24a43c5b3615ac0185acd1817554844ba1d145d1e380391ae2375` | `true` |
| `src/tlgp_001b_r2/world.py` | `1c9bd730e79c19e5036e26cf4a45f1463dc2194217ec5ebc06e42731ca364a7c` | `1c9bd730e79c19e5036e26cf4a45f1463dc2194217ec5ebc06e42731ca364a7c` | `true` |

Global `current_on_disk_equals_executed_for_all_r2_sources`: `true`

## B3 - AGENTS.md Governance Drift Repair

- Prior B3 report claim incorrect: `true`
- Short re-audit rejection verdict: `repair_rejected_forbidden_governance_drift_persists`
- Prior incorrect claim: the previous repair report claimed `git diff --ignore-space-at-eol -- AGENTS.md` was empty.
- Rejection reason: short re-audit found `AGENTS.md` still had forbidden governance drift from a whitespace-only EOF line, so the previous B3 status was not acceptable.
- B3-only cleanup performed: `true`
- Narrow command run: `git checkout -- AGENTS.md`
- HEAD blob after cleanup: `742c637e8390afbb5a3af363f0d5e1762bf5724b`
- Worktree blob after cleanup: `742c637e8390afbb5a3af363f0d5e1762bf5724b`
- Worktree blob equals HEAD blob after cleanup: `true`
- `git diff --ignore-space-at-eol -- AGENTS.md` result after cleanup: empty
- `git diff -w -- AGENTS.md` result after cleanup: empty
- `git status --short -- AGENTS.md` result after cleanup: empty
- Index empty after cleanup: `true`
- Stale `.git/index.lock` encountered: `false`
- Banking status: not banked; banking still requires B3-only short independent re-audit.

## Required Confirmations

- No official rerun: `true`
- No training rerun: `true`
- No replay rerun: `true`
- No scientific artifact modification by B3 cleanup: `true`
- No prereg modification: `true`
- No result scientific verdict mutation: `true`
- No trace mutation: `true`
- No TLGP-001A/R1 artifact mutation: `true`
- No 001C advance: `true`
- No git add/commit/push/tag/anchor: `true`
- No official bundle manifest update: `true`; no `.pre_repair` backup needed because no existing official manifest was overwritten.
- Banking still requires short independent re-audit: `true`

## Prereg Readback

- Expected canonical SHA256: `6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7`
- Recomputed canonical SHA256: `6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7`
- Match: `true`
- Raw prereg bytes SHA256: `2a2c2217d61f2b598ff5a96aeabadad5a746b8b9b4bcc6caf781d2d7f6772b91`

## Official Result Readback

- Official result exists: `true`
- Official run task verdict: `tlgp001b_r2_official_full_run_completed`
- Official scientific verdict: `tlgp001b_r2_invalid_learnability_floor_failed`
- Official result SHA256: `3e0a2aaac4c76f6354ff9b4aef5c8c5e24aa0c8b349f11c7677ccc0ba23035ad`

## Trace Readback

- Trace file: `artifacts/TLGP-001B-R2/OFFICIAL_FULL_RUN/traces/official_trace.jsonl`
- Manifest trace SHA256: `f9d5f47854b91cc107230a2335b12c8c43dad6ffc82b34a2dee0da708ab6c0fd`
- Current trace SHA256: `f9d5f47854b91cc107230a2335b12c8c43dad6ffc82b34a2dee0da708ab6c0fd`
- Trace hash match: `true`
- Metric count: `766`

## What This Repair Does Not Prove

This repair does not prove TLGP-001B-R2, H0/H1, TLGP-001A downgrade, headroom survival, general meta-learner failure, theory failure, mechanism evidence, agency, selfhood, consciousness, emotion, autonomy, EGO readiness, runtime readiness, companion readiness, user benefit, or 001C authorization.

## Next Minimal Closed-Loop Action

B3-only short independent re-audit of `AGENTS.md` cleanup and corrected provenance repair report before banking.
