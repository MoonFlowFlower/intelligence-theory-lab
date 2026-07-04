# FSP-PUM-ENV-IDPROBE-001A — REPLAY-PARTITION-ORDER-FIX-001A Task Card

Status: DRAFT until operator banks this file; the checkpoint-commit act is the approval.
Drafted by: Claude (lab auditor role), 2026-07-04, at operator request, after the S3d
preflight STOP (`STOP_s3d_preflight_guard_failed`) and an independent same-agent RCA that
reproduced both hashes. Drafted BEFORE any fix code exists; the acceptance gate below is
pre-registered against the frozen banked hashes, which are the immovable reference.

Task ID: FSP-PUM-ENV-IDPROBE-001A-REPLAY-PARTITION-ORDER-FIX-001A

Layer: 2 — engineering implementation (replay-instrument defect repair). NOT mechanism,
learning, subjectivity, or consciousness layer. This card repairs a serialization/replay
defect; it produces no mechanism, gap, or environment-validity evidence.

Governing sources (READ-ONLY during this fix; editing any = blocking
governance-self-modification failure): `FSP-ENV-DESIGN-CONSTRAINTS-001A.md`,
`FSP-PUM-ENV-IDPROBE-001A-S3D-SHOULD-WIN-NULL-ENV-SPEC-001A.md` (§4 BASE-invariance
regression), execution plan, `frozen_design.json`, the ten frozen
`s3a_trajectory_set_manifest.json` set hashes and `trajectory_sets/set_*_recipe.json`.
This card does not narrow or reinterpret any of them; it makes regeneration faithful to
the streams they already froze.

## Problem Definition

The S3d preflight guard STOPped because
`src/fsp_pum_env/s3d_certificates.py::run_s3d_preflight_guards` computed
`regenerate_member_view_sha256(design, set_00)` = `6a411128b756...4900d05fb`, which does
not equal the banked `set_00.member_view_sha256` = `0077f0b7173a...9c0154`.

Reproduced root cause (independent same-agent RCA; both host anchors reproduced on a third
machine, numpy 2.2.6 / py3.10):

- At S3a bank time, `trajectory_sets.build_generation_specs` builds
  `partitions = {"train": {0,800}, "heldout": {800,200}}` in that INSERTION order, and
  `_hash_spec_streams` iterates `spec.partitions.items()` in insertion order. The banked
  `member_view_sha256` is therefore the hash of the stream concatenated **train-then-heldout**.
- The manifest is written by `_write_json(..., sort_keys=True)`, which recursively sorts
  all dict keys and thus stores the partition names **alphabetically** (`heldout` before
  `train`).
- On regeneration, `_spec_from_manifest_entry` rebuilds `spec.partitions` from the stored
  (alphabetized) JSON, preserving `{"heldout": ..., "train": ...}`. `_hash_spec_streams`
  then concatenates **heldout-then-train**, yielding a different SHA-256.

Every per-user member-view record is byte-identical between the two orderings; only the
partition concatenation order differs. Direct proof (set_00, full 1000 users × 300 turns):

```
hash(order = train, heldout) = 0077f0b7173a...9c0154   == banked_s3a         (TRUE)
hash(order = heldout, train) = 6a411128b756...0d05fb   == guard_regenerated  (TRUE)
```

This is a deterministic replay-order defect in the regeneration path. It is NOT:
- sealed-generator drift — `generator_code_hash` = `5db8e8035d8a...a3e244` is identical at
  the S3a bank commit `3bf24cc` and at HEAD; git log shows no commit has touched
  `simulator.py` or `trajectory_sets.py` since `3bf24cc`.
- the uncommitted S3d simulator additions — they are purely additive and BASE-neutral
  (every new branch is gated on `variant in _CONSTANT_CERT_VARIANTS`, which is False for
  `BASE`); set_00 is a `BASE` set, so its stream is unaffected by them.
- environment / floating-point nondeterminism — the FP risk pre-registered in the
  20260703B handoff is real but did NOT fire here; both anchors reproduced exactly on an
  independent numpy build purely by flipping order.

Bug scope: only MULTI-partition sets are affected (the ten frozen S3a REAL sets
set_00..set_09, each `train` + `heldout`). The S3d certificate sets are single-partition
(`{"train": {0,800}}`), so they are unaffected; the failure surfaces specifically in the
BASE-invariance regression, which regenerates a two-partition S3a set.

## Current Stage

S3d preflight guard STOP, before PART 0. Score exposure unchanged (chance-level
internal-validation only; no cert-cell / NULL / gap / heldout numbers exist). No
authorization beyond this defect repair: no PART 0 execution, no cert run, no NULL-env
run, no re-bank of any frozen value, no member / threshold / seed / budget motion, no EGO
mainline, no LLM/AIRI, no deployment.

## Hypothesis

H (partition-order drift): the entire mismatch is explained by partition concatenation
order induced by `sort_keys=True` serialization. Making regeneration order-faithful to the
generator's canonical partition order will make `regenerate_member_view_sha256` reproduce
the banked `member_view_sha256` for set_00 AND for all ten frozen sets, changing no banked
value.

Falsifier: if, after a pure order-canonicalization, ANY of the ten banked hashes fails to
reproduce, or any per-user record byte differs between orders, H is wrong — a second, real
drift exists → STOP `partition_order_not_sole_cause`, do not proceed, do not re-bank, open
a fresh RCA card.

## Baseline (order-invariance)

The fix is admitted only if it is provably an order-canonicalization that preserves
per-user bytes. Pre-register:

1. Order-invariance baseline: the regenerated member-view hash must be INVARIANT to the
   on-disk serialization order of partition keys, and must equal the generator's
   canonical-order hash (partitions in ascending `start_user_id`: `train`(0) before
   `heldout`(800)).
2. Per-user equality control: assert that the per-partition, per-user record stream is
   byte-identical under both key orders (isolating "order-only" difference). Already true
   at set_00 scope; the fix's test must assert it structurally.
3. Simpler-cause exclusions recorded so the fix cannot silently rescope: generator code
   identical (`generator_code_hash` match), Codex delta BASE-neutral, environment/numpy
   excluded (both anchors reproduced on numpy 2.2.6). If implementation discovers any of
   these is actually implicated, STOP and escalate rather than expanding scope.

## Ablation

- A. Order-flip fail-ability: with the fix in place, force `heldout`-first order and
  confirm the hash CHANGES away from banked. The guard must remain able to FAIL; a fix
  that makes it vacuously pass is rejected.
- B. Single-partition no-op: confirm S3d cert-set specs (single `train` partition) produce
  an identical member-view hash before and after the fix (the fix is a no-op for
  single-partition specs).
- C. Revert reproduces failure: removing the fix must reproduce the exact STOP (regenerated
  `6a411128...` vs banked `0077f0b7...`), proving the fix is the resolving change.

## Trace / Replay Requirement

- Produce a NEW machine-readable replay artifact (do NOT overwrite the preserved failure
  artifacts) recording, for all ten sets set_00..set_09: banked_hash,
  regenerated_hash_before_fix, regenerated_hash_after_fix, canonical partition order used,
  per-partition record counts, and per-set match booleans.
- Regeneration must reconstruct from manifest recipe + `frozen_design.json` + generator
  code only — no set files, no hidden future state (consistent with S3D spec §4
  "regeneration, not set files").
- Preserve `artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_preflight_guard_report.json` and
  `s3d_preflight_guard_failure_manifest.json` verbatim. If the re-run guard writes to the
  same path, copy the failed report to `*_v1` FIRST (handoff §2.4 defect-preservation
  rule).

## Acceptance Gate (all required)

1. Ten-set reproduction: after the fix, `regenerate_member_view_sha256` reproduces the
   banked `member_view_sha256` EXACTLY for all ten frozen sets set_00..set_09.
2. Guard passes cleanly: `run_s3d_preflight_guards` returns `guards_passed` with
   `base_invariance_regression.passed = true`, and the two new-variant guards and two ideal
   micro-guards still pass unchanged.
3. Zero frozen-value change: `git diff` shows no modification to any banked hash, recipe,
   or frozen artifact value. Partition-key byte-layout in the manifest is NOT rewritten
   (see design constraint below). EOL-only churn, if any, is separated and not bundled.
4. Test growth: full `tests/fsp_pum_env` suite passes and item count strictly increases
   from the current 82; new tests cover baseline (1)+(2) and ablation A.
5. Isolation: production change confined to the regeneration/hash path in
   `src/fsp_pum_env/trajectory_sets.py`; `simulator.py` generation behavior untouched; the
   `generator_code_hash` change (from any edit to `trajectory_sets.py`) is disclosed and
   explained (it hashes file bytes, not behavior).

## Design Constraint (binding): read-side canonicalization only

The fix MUST be read-side: canonicalize partition iteration order at regeneration/hash time
(iterate partitions in ascending `start_user_id`, or otherwise reconstruct the generator's
canonical generation order) regardless of the stored dict order. A write-side fix
(e.g. storing partitions as an ordered list) is FORBIDDEN here because the ten banked
manifests already store the alphabetized order; rewriting them to a new layout would mutate
frozen artifacts. The banked hashes are the immovable reference; the instrument must be made
to reproduce them, not vice versa.

Two acceptable read-side shapes (non-binding; the acceptance gate is what binds):
- (a) In `_hash_spec_streams` / the regeneration path, iterate `spec.partitions` sorted by
  `start_user_id` ascending.
- (b) In `_spec_from_manifest_entry`, rebuild the partitions mapping in ascending
  `start_user_id` order so downstream iteration is canonical.

## Claim Ceiling

Bounded replay/serialization-defect repair evidence only. Reproduces the frozen banked
streams; does not create, re-open, strengthen, or re-interpret any S3a/S3b/S3c/S3d result.
No environment-validity, baseline-power, gap, mechanism, learning, adaptation, agency,
autonomy, or EGO/companion claim. Does not prove cross-platform floating-point
reproducibility (separate, still-open risk; unpinned numpy). Guard passing merely unblocks
the pre-registered PART 0 gate, which adjudicates compute independently; it does not
authorize PART 0 or any certificate claim.

## Stop Conditions

- `partition_order_not_sole_cause`: any of the ten banked hashes fails to reproduce after
  pure order-canonicalization, or any per-user record byte differs between orders. Halt,
  do not re-bank, escalate to new RCA.
- `fix_requires_patching_frozen_evidence`: reproduction would require changing any banked
  value, rewriting a frozen manifest layout, or loosening/removing a guard. Halt (forbidden).
- `scope_expansion`: the fix cannot be isolated to the regeneration path without altering
  `simulator.py` generation behavior. Halt, request a scope decision.
- Sandbox pytest carries zero evidential force (handoff §2.5); the acceptance artifact must
  be produced on the host, host-verified.

## Rollback Plan

- The fix is a small isolated diff to `trajectory_sets.py` (+ new tests). No banked artifact
  is touched, so rollback is clean with zero evidence loss.
- Before operator bank: discard the uncommitted working-tree diff
  (`git checkout -- src/fsp_pum_env/trajectory_sets.py` and remove the new test/artifact
  files). This restores the exact pre-fix STOP state (regenerated `6a411128...` vs banked
  `0077f0b7...`), reproducible via ablation C.
- After operator bank: `git revert` the fix commit (single-file revert), which returns the
  regeneration to the failing order. Preserved failure artifacts remain intact throughout.

## Expected Changed Files

- `src/fsp_pum_env/trajectory_sets.py` — read-side partition-order canonicalization (ONLY
  production file).
- `tests/fsp_pum_env/<new test file>` — order-invariance, canonical-equality, and
  fail-ability (ablation A) tests.
- NEW artifacts under `artifacts/FSP-PUM-ENV-IDPROBE-001A/` — ten-set reproduction report
  (e.g. `s3d_base_invariance_replay_order_fix_report.json`) and the re-run guard report
  (preserving the failed one via `*_v1` if the path collides).

## Forbidden Changes

- Any modification to `s3a_trajectory_set_manifest.json` banked hashes, `set_*_recipe.json`,
  or any frozen artifact VALUE; any rewrite of the manifest partition-key layout.
- Re-banking set_00 (or any set) reference to the wrong-order hash `6a411128...`.
- Loosening, disabling, or making vacuous the BASE-invariance guard or the
  new-variant / ideal micro-guards.
- Any change to `simulator.py` generation behavior; any threshold / member / seed / budget
  motion in the S3D spec or frozen design.
- A global `sort_keys` toggle or any change that alters other artifacts' byte layout beyond
  the partition-order fix (avoid collateral churn / schema fragmentation).
- Governance self-modification: editing the S3D spec, execution plan, constitution, or
  frozen design to accommodate the fix.
- EGO mainline, LLM/AIRI integration, deployment, external services, credentials.

## Evidence Appendix (RCA reproduction, for independent re-check)

- Banked set_00 `member_view_sha256`: `0077f0b7173a34b2c6f3dfaf6081386ade3ee626d4a2369b76b6a619689c0154`
- Guard regenerated (heldout,train), verbatim from `s3d_preflight_guard_report.json`: `6a411128b756db8cd8d9de34d47d3fb85747a68930078449f5e5c014900d05fb`
- `generator_code_hash` (S3a bank `3bf24cc` and HEAD, identical): `5db8e8035d8a805701e68900025b55cc0273e3991e315dd374314fb7dea3e244`
- set_00 spec: partitions `train{start 0, count 800}` + `heldout{start 800, count 200}`,
  `turns_per_user = 300` (1000 users × 300 = 300000 records).
- Reproduction method: regenerate each user's member-view chunk independently (RNG seeds
  derive only from `master_seed` + partition + `user_id`; validated byte-identical to the
  serial `_hash_spec_streams` on a 5-user mini-set), then hash the concatenation under each
  partition order. `hash(train,heldout)` == banked; `hash(heldout,train)` == guard value.
