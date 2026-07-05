# Codex execution prompt — TLGP-001B-R2 provenance bank (Card R1)

Paste everything below the line into Codex, running in the `intelligence-theory-lab`
repo on the real machine (git + git-lfs available).

---

You are executing an AUTHORIZED, BOUNDED provenance-banking task. The governing
task card is `docs/task_cards/TLGP-001B-R2-PROVENANCE-BANK-001A.md` (revision R1) —
read it first and obey it exactly. This authorizes exactly ONE local commit. It does
NOT authorize a re-run, any source edit, scope expansion, or any push.

## Absolute guardrails — violate any ⇒ STOP, write `artifacts/TLGP-001B-R2/failure_manifest.json`, do NOT commit
- Do NOT edit ANY file under `src/tlgp_001b_r2/`. Bank the executed bytes unmodified.
  In particular do NOT "fix" `official_full.py` — the B2 verifier fix is a SEPARATE
  card (`TLGP-B2-FUTURE-PIN-FIX-001A`) and is OUT OF SCOPE here.
- Do NOT re-run/retrain. Do NOT modify `result.json`, `trace_manifest.json`,
  `official_trace.jsonl`, `verdict.py`, `prereg.json`, or any recorded metric/artifact.
- Do NOT `git add -A` / `git add .`. Stage only the explicit paths in Step 5.
- Do NOT touch `AGENTS.md`, `CLAUDE.md`, or any global config. The ONLY allowed
  `.gitattributes` action is restoring it to HEAD (Step 1).
- NEVER inline the LFS trace content into a git blob. NEVER run `scripts/push.*` or
  any push/PR/remote operation.

## Preconditions — STOP if any fails
1. `git rev-parse HEAD` == `b4ee157a01caef34c598bbeb3ac5ed1bb9b90f24` (or a descendant
   on the intended branch — if different, confirm with operator before proceeding).
2. `git lfs version` succeeds. If git-lfs is NOT installed, STOP and ask the operator
   to install it. Do not proceed without it.
3. Trace is an LFS object in HEAD:
   `git show HEAD:artifacts/TLGP-001B-R2/OFFICIAL_FULL_RUN/traces/official_trace.jsonl`
   begins `version https://git-lfs.github.com/spec/v1`, oid
   `f9d5f47854b91cc107230a2335b12c8c43dad6ffc82b34a2dee0da708ab6c0fd`, size 507348934.

## Authoritative source whitelist (EXACTLY these 9; from `OFFICIAL_FULL_RUN/source_manifest.json:delivered_source_hashes`)
```
src/tlgp_001b_r2/__init__.py          3c61963f7e387ea7f1dabc8ae31d725f8d29b57d525445d62bec017a748d183b
src/tlgp_001b_r2/harness.py           6b32e47ef8bf9ad91716418ede7611ff011a0bdaa5a1c37ebc1b739c580c576f
src/tlgp_001b_r2/lower_reference.py   cd701b2f4adcf9d8c66f28f0e797cdf748a7f4560c682953829b99eb85d28cf6
src/tlgp_001b_r2/meta_learners.py     358d2bb2449f88ff5c73de52fcabcbba17f40b22dabc5c484f7b67da627e1b6f
src/tlgp_001b_r2/official_full.py     1101ef25de3c60e30d1e42343d543dc6e3fd6d49aedfac1bf2e974a3f46ff6f3
src/tlgp_001b_r2/preregistration.py   6a5a0273e7c3b0c2cce031dcf2b495646d87ecea7630d725c84def8f9ce27480
src/tlgp_001b_r2/splits.py            ca2852a1ca69ba5277872bf5b0780163d0c79fbf0b5b2c7075bb740ef9981ad5
src/tlgp_001b_r2/verdict.py           ac80b06083b24a43c5b3615ac0185acd1817554844ba1d145d1e380391ae2375
src/tlgp_001b_r2/world.py             1c9bd730e79c19e5036e26cf4a45f1463dc2194217ec5ebc06e42731ca364a7c
```

## Procedure (run in order; STOP on any gate failure)

**Step 0 — preflight readback.** Record `git rev-parse HEAD`, current branch,
`git lfs version`, and full `git status --porcelain`.

**Step 1 — restore `.gitattributes` to HEAD.** If `git diff -- .gitattributes` is
non-empty (the known trailing-CR drift on the LFS-rule line), run
`git checkout -- .gitattributes`. Confirm the diff is now empty and
`git check-attr filter -- artifacts/TLGP-001B-R2/OFFICIAL_FULL_RUN/traces/official_trace.jsonl`
reports `filter: lfs`.

**Step 2 — ensure the trace is a clean, unmodified LFS pointer.** The trace is
ALREADY committed as a pointer at HEAD; the bank commit must NOT change it. If
`git status --porcelain -- artifacts/TLGP-001B-R2/OFFICIAL_FULL_RUN/traces/official_trace.jsonl`
is non-empty, restore from LFS (`git checkout -- <trace>` or `git lfs checkout <trace>`).
Then verify BOTH: `sha256sum <trace>` ==
`f9d5f47854b91cc107230a2335b12c8c43dad6ffc82b34a2dee0da708ab6c0fd`, AND
`git status --porcelain -- <trace>` is EMPTY. If you cannot make it clean+matching → STOP.

**Step 3 — source ingress verification (B1).** Confirm the on-disk set of `*.py`
under `src/tlgp_001b_r2/` (excluding `__pycache__`) is EXACTLY the 9 whitelist paths —
no missing, no extra. Compute sha256 of each and compare to the whitelist. Write
`artifacts/TLGP-001B-R2/source_ingress_manifest.json` as
`[{ "path","size","sha256","matches_delivered": bool }, ...]`. Any missing / extra /
mismatch → STOP.

**Step 4 — write `artifacts/TLGP-001B-R2/bank_source_reverification.json` (B4):**
```json
{
  "pre_run_delivery_pin_exists": false,
  "b2_original_gate_status": "tautological_not_closable_for_this_run",
  "posthoc_source_reverification_scope": "current_ingested_equals_runtime_recorded_source_only",
  "may_claim_delivered_equals_executed_for_original_run": false,
  "verdict_validity_basis": "trace_plus_frozen_prereg_clean_room_replay_independent_of_source_identity",
  "per_file": [ /* from Step 3: path,size,sha256,matches_delivered */ ]
}
```

**Step 5 — scoped stage (explicit paths ONLY; never `-A`):**
```
git add -- src/tlgp_001b_r2/ \
           artifacts/TLGP-001B-R2/ \
           artifacts/CLAUDE-INDEPENDENT-TLGP-001B-R2-OFFICIAL-FULL-RUN-AUDIT-001/ \
           artifacts/CLAUDE-INDEPENDENT-TLGP-001B-R2-HARNESS-SMOKE-001-AUDIT-001/
```

**Step 6 — pre-commit gates (ALL must pass; else `git reset` to unstage, STOP, failure_manifest):**
- a. `git diff --cached --name-only` contains ONLY paths under `src/tlgp_001b_r2/`,
  `artifacts/TLGP-001B-R2/`, or `artifacts/CLAUDE-INDEPENDENT-TLGP-001B-R2-*`. No
  `AGENTS.md`, `CLAUDE.md`, `.gitattributes`, or any other path.
- b. Trace stays a pointer: if `official_trace.jsonl` appears in the staged set,
  `git cat-file -p :artifacts/TLGP-001B-R2/OFFICIAL_FULL_RUN/traces/official_trace.jsonl | head -c 45`
  == `version https://git-lfs.github.com/spec/v1`. (Best case: it is NOT staged at
  all, because it is unchanged.) If it is staged as raw JSONL rows → unstage, STOP.
- c. No source content changed: for each of the 9 files,
  `git cat-file -p :<path> | sha256sum` == its whitelist hash.
- d. Size guard: no staged file is a non-LFS blob larger than 10 MB. If one is, STOP
  and report it for operator decision (do not auto-commit).

**Step 7 — commit (LOCAL only, NO push).** The commit message MUST contain, verbatim,
this exact banking statement (do not paraphrase):
```
TLGP-001B-R2 official full run produced bounded INVALID due to learnability-floor failure under frozen prereg sha 6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7.
```
Recommended form:
```
git commit -m "docs(bank): TLGP-001B-R2 official full run — bounded INVALID (learnability-floor)" \
           -m "TLGP-001B-R2 official full run produced bounded INVALID due to learnability-floor failure under frozen prereg sha 6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7."
```
Do NOT push.

**Step 8 — post-commit verification.** Record the new commit hash; run
`git show --stat <hash>`; confirm the trace entry in the commit is the pointer
(`git cat-file -p <hash>:artifacts/TLGP-001B-R2/OFFICIAL_FULL_RUN/traces/official_trace.jsonl | head -3`).
Optional: if a from-trace replay entrypoint exists and runs WITHOUT retraining, run it
and confirm `replay_exact` / verdict unchanged; otherwise note that the Step-2 trace
byte-identity (sha256 == oid) already guarantees equivalence to the audited run.

## On any STOP
Write `artifacts/TLGP-001B-R2/failure_manifest.json`
`{ "failed_step", "reason", "observed", "expected", "git_status" }`, do NOT commit,
leave the worktree as found, and report.

## Final report (required)
- Verdict: `banked` | `stopped(<reason>)`
- New commit hash + staged file list (with counts)
- Gate results: Steps 1–6 each pass/fail
- Trace: pointer preserved? oid match? not inlined?
- Source: 9/9 match delivered hashes?
- Artifacts written: `source_ingress_manifest.json`, `bank_source_reverification.json` (+ `failure_manifest.json` if stopped)
- Confirm: no `src/tlgp_001b_r2/` byte edited; no push; B2 left OPEN (recorded), not fixed here
- Claim ceiling (verbatim): bounded offline preservation of one negative result only;
  NOT mechanism / learning / transfer / agency / self / subjectivity / AGI / EGO.
