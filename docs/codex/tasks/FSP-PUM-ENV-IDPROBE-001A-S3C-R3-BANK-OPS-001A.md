# FSP-PUM-ENV-IDPROBE-001A — S3C-R3-BANK-OPS-001A (bank execution card)

Status: ACTIVE on operator paste. Drafted by Claude (lab auditor role) at operator
instruction, 2026-07-03, after the S3c-R3 audit verdict
ACCEPT_with_required_pre-bank_additions (no blocking issues). Disclosed in-file.

ROLE EXCEPTION (one-time): the operator initially authorized Codex to execute the
bank COMMIT for S3c-R3 under this card. SUPERSEDED same day: the operator executes
the bank personally (standard role contract restored; the Codex git exception was
never exercised). PART A artifacts were drafted by Claude (auditor) at operator
instruction, disclosed in-file. `git push` remains OPERATOR-ONLY. Rung1 session is
closed and `.git/index.lock` has been removed by the operator.

ANTI-IDLE: restating or re-describing existing artifacts = failure. Success = exactly
two new JSON artifacts + one scoped commit + the report format at the end, with fresh
sha256 values and gate results.

## Scope

- PART A: write 2 NEW artifacts (pre-bank additions required by the R3 audit).
- PART B: verification gates. Any gate failure = STOP + report. Never repair.
- PART C: one scoped commit. Nothing else.

Forbidden throughout:

- modifying ANY existing file (code, tests, artifacts, docs, recipes, logs);
- `git add -A`, `git add -u`, `commit --amend`, rebase, branch ops, tag, push;
- touching `scripts/`, `.gitattributes`, `docs/task_cards/`, TLGP paths, or any
  `docs/codex/tasks/` file other than committing THIS card;
- deleting or renaming anything (incl. `no_models_persisted_due_projection_stop.json`);
- patching a failed gate into a pass; changing thresholds; adding tests or code.

## PART A — two new artifacts

### A1. artifacts/FSP-PUM-ENV-IDPROBE-001A/s3c_r3_first_sweep_defect_note.json

Exact field set (values in <> to fill; everything else verbatim):

```json
{
  "artifact": "s3c_r3_first_sweep_defect_note",
  "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
  "stage": "S3c-R3",
  "defect": "first completed R3 sweep's CPU-h meter summed model fit/predict wall-clock only, excluding feature/sequence materialization; nonconformant to the 001C accounting definition (CPU-h = per-config whole wall-clock at threads=1)",
  "discovery": "found by executor's own artifact-validation pass before reporting; not caught by pre-run tests",
  "remedy": "accounting corrected in src/fsp_pum_env/battery/obs_decoders.py; regression tests added; full 40-config rerun under corrected meter, run_id s3c-decoder-tuning-2026-07-03T14:23:20Z",
  "incentive_direction": "defect undercounted CPU-h; the correction counts more time and is against executor interest w.r.t. the 30.0 CPU-h runtime guard",
  "evidence_loss": {
    "v1_tuning_report": "overwritten by rerun, unrecoverable",
    "v1_stdout_stderr_logs": "overwritten by rerun, unrecoverable",
    "v1_total_cpu_hours": "<number ONLY if recoverable from preserved bytes or session scrollback, else \"unknown\">",
    "v1_scores_bitwise_identical_to_rerun": "<true/false ONLY if verifiable, else \"unknown\">",
    "recovered_values_provenance": "<\"session_scrollback_not_artifact_grade\" if any value above was recovered from scrollback; null if nothing recovered>"
  },
  "corrected_code_identity": {
    "code_path_hash": "<copy verbatim from s3c_battery_manifest.json>",
    "component_code_hashes": "<copy the base/obs_decoders/seq_models object verbatim from s3c_battery_manifest.json>"
  },
  "process_rule_violated": "preserve failure artifacts (lab evidence contract); defective-run outputs should have been renamed to versioned *_v1 files before rerun, per the s2_tractability_report v2/v3/v4 precedent",
  "process_rule_forward": "any future instrument-defect discovery: preserve the defective outputs under versioned names BEFORE rerunning",
  "claim_ceiling": "process defect record only; no performance, baseline-power, environment-validity, mechanism, learning-capability, agency, or EGO claim"
}
```

Honesty rules: fill "unknown" where you cannot verify. Do NOT reconstruct v1 numbers
from memory without the `recovered_values_provenance` flag. Do NOT soften
`process_rule_violated`.

### A2. artifacts/FSP-PUM-ENV-IDPROBE-001A/s3c_r3_fp_nondeterminism_declaration.json

```json
{
  "artifact": "s3c_r3_fp_nondeterminism_declaration",
  "task_id": "FSP-PUM-ENV-IDENTIFIABILITY-PROBE-001A",
  "stage": "S3c-R3",
  "scope_members": ["obs_decoder_logreg", "obs_decoder_gbt", "obs_decoder_gru", "seq_full_history_no_action_conditioning", "seq_window_with_action_conditioning_W15_no_cross_session_persistence"],
  "determinism_basis": "deterministic_training_recipe: per-member config_seed + frozen S3a trajectory sets + code identity (component_code_hashes in s3c_battery_manifest.json) + threads=1 + framework_versions as recorded in s3c_battery_manifest.json",
  "declared_fp_nondeterminism_sources": [
    "sklearn lbfgs / HistGradientBoosting floating-point reduction order under BLAS/threadpool variation",
    "torch CPU kernel implementation differences across builds and platforms",
    "compiler and BLAS library differences across hosts"
  ],
  "reproducibility_claim": "bitwise reproducibility is expected only on same platform + same framework versions + threads=1; cross-platform replay tolerance is NOT declared here and must be adjudicated at recipe consumption time (S3d/S5)",
  "recipe_files_sha256": {
    "obs_decoder_logreg_selected_recipe.json": "c331b27db21ae4d2d9e6d6e94e35110565b8786b134bcaf1be50a8e7dad76388",
    "obs_decoder_gbt_selected_recipe.json": "f2a091c9dc3b93a2b258ee3dfb4bf5515911cafc8b9b2564613b2f10d9e338fc",
    "obs_decoder_gru_selected_recipe.json": "8341f5d1221817258f5696bdf08feb663c03e6345aa3ec84b925350b8ed30bd1",
    "seq_full_history_no_action_conditioning_selected_recipe.json": "723bf89d13af3d154b2f9ebf208998f0d2924942b343864a26cb2a04d0b5deb5",
    "seq_window_with_action_conditioning_W15_no_cross_session_persistence_selected_recipe.json": "37ae0e00df2acb5aabfe663a141a2d59096985d9f31393105f448b2565a504b3"
  },
  "claim_ceiling": "declaration only; no reproducibility evidence claim"
}
```

Recipe files themselves must NOT be modified (their sha256s are referenced by the
manifest and the sweep stdout log).

## PART B — verification gates (all on host; any failure = STOP + report)

- B1 Freeze stack: python blob-sha (no git needed) of the SEVEN frozen docs equals the
  full values pinned in the R3 prompt; prefixes: card `0a5e38a5dbe9` / constitution
  `882a68de2973` / execution plan `c07eec2ac384` / frozen_design `32d2cbd538f3` /
  001A `2da9e5693255` / 001B `bfabd9ebfbd4` / 001C `2940db67ad3b`. F2 vocabulary
  sha256 == `3a08b3b5a387ec9327e2cf4410576fbd731903ddf8b98f44d121b2f5f708b391`.
- B2 R3 artifact sha256 re-verify on host, in particular
  `s3c_battery_manifest.json` == `0f711c8b307f9cda390d595e2e940dd96404ac9b251093805d866c6b4848333a`
  (this closes the auditor's sandbox-FUSE staleness item; report PASS/FAIL explicitly),
  plus the tuning report `abe54625…`, collision record r3 `26f6a6f8…`, and the five
  recipe sha256s listed in A2.
- B3 `python -m pytest tests/fsp_pum_env -q` == 72 passed (this card adds no tests).
- B4 Git preflight: no `.git/index.lock`; current branch `codex/meta-theory-scaffold`;
  `git rev-parse HEAD` starts with `567af96` (S3c-R2 STOP + 001C bank). If
  `git status --porcelain` shows mass bogus staged D/M entries (poisoned shared
  index), run exactly `git reset` (mixed, no pathspec) ONCE and re-check; if still
  bogus, STOP. If HEAD != 567af96*, STOP (do not commit on top of an unexpected head).
- B5 Both new JSONs parse; required fields present; compute and record their sha256.

## PART C — single scoped commit

- C1 Stage EXPLICIT paths only:

  ```
  git add src/fsp_pum_env tests/fsp_pum_env artifacts/FSP-PUM-ENV-IDPROBE-001A docs/research/SESSION-HANDOFF-FSP-20260703.md docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3C-R3-BANK-OPS-001A.md
  ```

- C2 Review `git status --porcelain`: the staged set must contain ONLY — modified
  `src/fsp_pum_env/battery/obs_decoders.py`; modified/new
  `tests/fsp_pum_env/test_s3c_obs_decoders.py`; new/updated files under
  `artifacts/FSP-PUM-ENV-IDPROBE-001A/` (R3 outputs, logs, the two PART A notes);
  the handoff file; this card. Zero deletions. No `__pycache__`, no TLGP paths, no
  `scripts/`. Anything unexpected → `git reset` + STOP + report the porcelain output.
- C3 Commit with exactly this message:

  ```
  S3c-R3 BANK: corrected 40-config sweep (15.0295/30.0 CPU-h, runtime guard ok; accounting conformance repair per 001C) + first-sweep defect note + FP nondeterminism declaration; audited ACCEPT_with_required_pre-bank_additions 2026-07-03; banked by operator (S3C-R3-BANK-OPS-001A)
  ```

- C4 Post-commit verify: `git show --stat HEAD` (paste into report);
  `git rev-parse HEAD^` starts with `567af96`; `git ls-tree` blob shas of the seven
  frozen docs UNCHANGED vs B1 pins (the commit must not have touched them; beware
  CRLF: banked blobs are LF-normalized — compare against LF-normalized hashes);
  record blob shas of the two new artifacts.
- C5 DO NOT push. Report and stop. The operator pushes and, separately, decides the
  optional checkpoint-script FROZEN_FILES hardening (001A/B/C shas) as its own commit.

## Required report format

Commit sha + parent sha; `git show --stat` output; staged file list; sha256 of the two
new artifacts; B1–B5 gate results incl. the explicit manifest-sha PASS/FAIL; pytest
count; STOP conditions triggered (if any); claim ceiling; what this does not prove.

## Claim ceiling

Bank bookkeeping + process defect record + FP nondeterminism declaration only. No
heldout, baseline-power, environment-validity, headroom, mechanism, learning-capability,
agency, or EGO claim. S3d adjudicates baseline adequacy; S5/S6 adjudicate claims.
