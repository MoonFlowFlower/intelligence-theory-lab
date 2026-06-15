# EVIDENCE-ADMISSION-VERIFIER-001B-CALLABLE-PROVENANCE-REPAIR-001A

## Problem Definition

Verifier Kernel v0 calibration is blocked because a forged-provenance positive-control bundle was admitted for citation. This proves v0 can still be fooled by clean-looking provenance/control rows. Repair the standalone verifier so admission requires resolvable, callable, hash-pinned producer computation rather than trusting provenance row text.

## Stage / Layer

Engineering-governance / standalone evidence-admission verifier repair only.

## Mainline Target

None. Do not wire into Gate3, Gate4, integrated admission, bridge, runtime, or EGO mainline.

## Enabled Requirement

The only enabled path is the standalone CLI/library:

```powershell
python -m evidence_admission_verifier_001a <bundle_path> --out <artifact_dir>
```

## Real-Trigger Requirement

Before modifying verifier source, preserve the current blocked calibration evidence:

- `artifacts/evidence_admission_verifier_001a_real_bundle_calibration_001a/result.json`
- `artifacts/evidence_admission_verifier_001a_real_bundle_calibration_001a/readback.json`
- current v0 source/test file hashes
- current git status showing untracked v0/calibration files

After repair, rerun the same calibration set:

1. real false-pass bundle: `artifacts/ego_mainline_gate4_preflight_executable_001b`
2. real candidate bundle: `artifacts/gate4_replacement_002c_dynamic_partner_belief_pomdp_execution_001a`
3. candidate ablation with `claim_ceiling.txt` removed
4. forged-provenance positive control from the blocked calibration
5. at least one new positive control where `producer_function` exists but code hash or output digest is wrong

## Hypothesis

If the repair is meaningful, forged-provenance bundles must block because their `producer_function` / import path / code hash / input hash / output recomputation cannot be validated. Clean-looking rows alone must no longer be sufficient for admission.

## Strongest Baseline

A row-shape-only verifier that admits bundles when provenance rows contain `producer_function`, inputs, `run_id`, aggregation, and `code_path_hash` fields. Record that this baseline would admit the forged-provenance positive control.

## Ablation

Run the repaired verifier on copies of an otherwise valid callable fixture with each of the following corrupted independently:

- missing `producer_function`
- non-importable `producer_function`
- `producer_function` importable but not callable
- callable returns output inconsistent with recorded metric/digest
- `code_path_hash` mismatch
- input file hash mismatch
- aggregation rule mismatch
- `run_id` missing or reused where uniqueness is required

Each ablation must block for a specific computed reason.

## Trace / Replay

For every decision, write an artifact containing:

- verifier command
- bundle path
- output artifact path
- verifier source hashes
- input file hashes
- `producer_function` import path
- resolved source file path
- resolved code hash
- declared `code_path_hash`
- declared inputs
- computed input hashes
- `run_id`
- aggregation rule
- recomputed output digest / metric
- admit or block decision
- block reasons

## Computed-Evidence Gate

Admission must require executable verification, not static row acceptance.

For every required evidence row, verifier must:

1. parse `producer_function` as a module:function path or explicitly block unsupported format;
2. import and resolve the callable from repo source;
3. hash the callable source path or declared source file;
4. compare computed code hash against declared `code_path_hash`;
5. verify declared input paths exist;
6. compute input hashes and compare against declared input hashes when present;
7. call `producer_function` with declared inputs in a controlled temp/output context;
8. recompute the declared metric/digest or block if recomputation contract is absent;
9. verify aggregation rule is declared and supported;
10. reject report/verdict/result text as admission evidence unless backed by the callable path above.

Legacy bundles without callable manifests may block as `unsupported_schema` or `missing_callable_provenance`. Do not rewrite real historical bundles to make them pass in this repair task.

## Acceptance Gate

- Start-state hashes for v0 source/tests/calibration artifacts are recorded before edits.
- Existing scoped pytest passes.
- New callable-provenance tests pass.
- Forged-provenance positive control blocks.
- Wrong-code-hash positive control blocks.
- Wrong-output/digest positive control blocks.
- Result/report edit cannot override missing callable evidence.
- Real false-pass bundle is run through the repaired CLI and its decision is recorded.
- Real candidate bundle is run through the repaired CLI and its decision is recorded.
- Candidate ablation with removed `claim_ceiling.txt` still blocks for `missing_claim_ceiling` or equivalent.
- Verifier source is the only source area modified.
- No Gate3/Gate4/mainline/bridge/runtime files modified.

## Claim Ceiling

Standalone callable-provenance verifier repair and calibration only. No Gate validity, mechanism validity, integrated admission readiness, mainline effectiveness, agency, consciousness, emotion, autonomy, stable user benefit, or EGO readiness claim.

## Stop Condition

Stop and preserve blocker if:

- current untracked v0 files or calibration artifacts are missing;
- forged-provenance still admits after repair;
- verifier admits any row without resolving and calling `producer_function`;
- `producer_function` can be non-importable but still pass;
- `code_path_hash` mismatch can pass;
- output/digest mismatch can pass;
- tests rely on static expected-verdict dictionaries;
- repair requires modifying real Gate3/Gate4/mainline artifacts;
- real candidate is edited to satisfy verifier instead of being classified as-is.

## Rollback Plan

If repair fails, keep the pre-repair blocker evidence and write a repair-blocked result artifact. Revert partial source changes unless they are required to preserve the failing evidence. Do not remote-anchor a failed repair as success.

## Changed Files Allowed

- `docs/codex/tasks/EVIDENCE-ADMISSION-VERIFIER-001B-CALLABLE-PROVENANCE-REPAIR-001A.md`
- `src/evidence_admission_verifier_001a/**`
- `tests/test_evidence_admission_verifier_001a.py`
- `tests/test_evidence_admission_verifier_001b_callable_provenance_repair_001a.py`
- `artifacts/evidence_admission_verifier_001b_callable_provenance_repair_001a/**`

## Allowed To Preserve From Previous Untracked State If Hashes Match Start Readback

- `docs/codex/tasks/EVIDENCE-ADMISSION-VERIFIER-001A.md`
- `artifacts/evidence_admission_verifier_001a_real_bundle_calibration_001a/**`

## Forbidden Files

- Gate3 source or artifacts except read-only input bundles
- Gate4 source or artifacts except read-only input bundles
- integrated admission source
- bridge/runtime/mainline files
- unrelated evidence harness files
- unrelated tests

## Auto-Remote-Anchor

Conditional.

Remote-anchor only if:

- forged-provenance positive control blocks;
- wrong-code-hash positive control blocks;
- wrong-output/digest positive control blocks;
- real false-pass bundle and real candidate bundle are rerun and recorded;
- all scoped tests pass;
- changed files are within allowlist;
- worktree is clean after commit;
- local HEAD, remote branch HEAD, local tag, and remote tag all exactly match.

If any stop condition triggers, do not remote-anchor as a successful verifier boundary. Preserve blocker evidence only.
