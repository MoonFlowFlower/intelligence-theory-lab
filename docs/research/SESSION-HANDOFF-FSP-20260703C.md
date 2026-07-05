# SESSION-HANDOFF-FSP-20260703C — S3d partition-order replay defect repaired + banked (80bfad4); PART 0 compute-projection RUNNING

- Session scope: fresh Claude session, auditor role. Received the S3d preflight STOP (BASE-invariance partition-order guard failure) → independent same-agent RCA (reproduced BOTH hashes on a 3rd machine by flipping partition order) → drafted the fix task card → Codex implemented a read-side fix → Claude audited ACCEPT (blocking=none) → operator banked **80bfad4** → dispatched Codex the S3d PART 0 compute-projection gate (now RUNNING). Roles intact: Codex implements (NO git), Claude audits + drafts governance, operator banks/pushes.
- Claim ceiling: unchanged. `80bfad4` is a replay/serialization-defect repair plus the S3d preflight instrument; it is NOT S3d evidence. Zero certificate, NULL, environment-validity, baseline-power, gap, mechanism, learning, agency, or EGO claim. First claim-bearing event remains S5, adjudicated in S6.
- Next-session reading order: this file → `docs/research/SESSION-HANDOFF-FSP-20260703B.md` (STILL authoritative for S3a–S3c history AND all S4 / Track-T / L-005 / loose-end obligations — this handoff does NOT supersede those) → memory `fsp-route-program-001a` + `itl-bank-workflow-operator-run` + `itl-git-sandbox-constraints` → `docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-SHOULD-WIN-NULL-ENV-SPEC-001A.md` → `docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-REPLAY-PARTITION-ORDER-FIX-001A.md`.

## 1. State (end of this session)

- **HEAD = `80bfad4`** (branch `codex/meta-theory-scaffold`), new this session; replaces `f2c0b3a`'s "S3d RUNNING" status.  Commit = 13 files, 1764 insertions(+), 4 deletions(−); porcelain gate PASS (zero `D` lines; staged set == the 13-file scoped list); no frozen value changed; broad pre-existing EOL churn was left unstaged.
- **PUSH STATUS = VERIFY.** `80bfad4` was committed host-side; a push was not observed in-session. New session: compare `git --no-pager rev-parse HEAD` vs `git --no-pager rev-parse origin/codex/meta-theory-scaffold`; push if intended (PAT rotate per `itl-git-sandbox-constraints`). The handoff file 20260703C itself is uncommitted DRAFT until the operator banks it (may bundle with the PART 0 bank).
- `80bfad4` contents:
  - `src/fsp_pum_env/simulator.py` — 2 BASE-neutral cert-only variants (`degenerate_should_win_constant_none` / `_saturated`), gated on `_CONSTANT_CERT_VARIANTS`.
  - `src/fsp_pum_env/s3d_certificates.py` — S3d preflight guard + cert-set builders + `run_s3d_part0_projection`.
  - `src/fsp_pum_env/trajectory_sets.py` — the partition-order fix + `write_partition_order_replay_fix_report`.
  - `tests/fsp_pum_env/` — `test_s3d_certificates.py`, `test_s3d_cert_variants.py`, `test_replay_partition_order_fix.py` (suite 82 → 86).
  - `artifacts/FSP-PUM-ENV-IDPROBE-001A/` — `s3d_collision_record_001a.json`; `s3d_preflight_guard_report.json` (**guards_passed**); `s3d_preflight_guard_report_v1.json` (preserved FAIL); `s3d_preflight_guard_failure_manifest.json` (+ `_v1`, preserved); `s3d_base_invariance_replay_order_fix_report.json` (10-set report).
  - `docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-REPLAY-PARTITION-ORDER-FIX-001A.md` (fix card).
- **S3d PART 0 compute-projection: Codex RUNNING** (dispatched this session). No artifacts yet; nothing to audit yet.

## 2. The defect + fix (banked in 80bfad4)

- Defect: the BASE-invariance preflight guard STOPped because `regenerate_member_view_sha256(set_00) = 6a411128… ≠ banked 0077f0b7…`. Root cause (reproduced on an independent numpy-2.2.6 build, BOTH anchors): the S3a manifest is written by `_write_json(..., sort_keys=True)`, which alphabetized the partition names (`heldout` before `train`); regeneration replayed that stored order and concatenated **heldout-then-train**, whereas the banked stream was **train-then-heldout**. Per-user records are byte-identical; only partition concatenation order differed. `hash(train,heldout)=0077f0b7=banked`; `hash(heldout,train)=6a411128=guard value`.
- Ruled out (each verified): generator drift (`generator_code_hash 5db8e803…` identical at the S3a bank `3bf24cc` and HEAD; no commit touched `simulator.py`/`trajectory_sets.py` between); environment/FP nondeterminism (both anchors reproduced EXACTLY on an independent build); the cert-only simulator additions (BASE-neutral — set_00 is a `BASE` set).
- Fix (READ-SIDE ONLY): `_partition_items(..., "canonical")` iterates partitions sorted by `(start_user_id, count, name)`; regenerate/hash default to `"canonical"`. `_write_json` and `to_json_dict` UNCHANGED — the ten frozen manifests are NOT rewritten (canonical order == the original generation order for all ten, so banked hashes reproduce with zero frozen-value change).
- Audit = ACCEPT, blocking=none. Independent corroboration: committed-HEAD == worktree == fix-report for all 10 banked hashes, and report-after == committed; a FRESH set_09 reproduced under canonical order with pristine HEAD code == committed banked; guard report (host-authoritative Read) = `guards_passed`, base regen == banked, `new_variant [true,true]`, `ideal [true,true]`; `_v1` artifacts sha-match the original FAIL (`18809a54…` / `10abebcd…`); production change confined to `trajectory_sets.py`.
- Non-blocking (carry forward): (a) the guard's own `code_path_hash` (`2f96d8dec…`) covers only `s3d_certificates.py`+`simulator.py`, NOT `trajectory_sets.py`; the fix-report's `generator_code_hash` (`9ac30342…`) does record it. (b) live `generator_code_hash` diverged from the banked recipes' `5db8e803…` → `9ac30342…` (behavior-preserving; a future S3a regen would record the new hash). Neither weakens the member_view_sha256 evidence.

## 3. Banking workflow (BINDING; new decision this session)

Operator considered and DECLINED Codex-self-bank. Settled flow: Codex implements and MAY emit a no-git BANK-OPS proposal (exact file list + per-file sha256 + HEAD-pin + scoped PowerShell script) but NEVER runs git; Claude audits the returned output; on ACCEPT Claude MUST emit the ready-to-run scoped bank script; the operator runs it. Bank-script discipline (reaffirmed from 20260703B §2.1): remove a stale `.git/index.lock` ONLY if no git process is live → HEAD-pin gate → `git reset` → explicit `git add -- <paths>` → porcelain gate (zero `D` lines AND staged == expected via `Compare-Object`) → `git commit` → `show --stat`.

**Operational lesson (new, important):** do NOT run sandbox/FUSE `git` against this repo. A sandbox `git status` this session left an unremovable `.git/index.lock` (FUSE unlink "Operation not permitted") that blocked ALL host git until the operator deleted it host-side. For provenance/inspection from the sandbox use the Read tool (host-authoritative), `git show HEAD:<path>` (object store), and `git archive HEAD` — and treat sandbox `git status` / working-tree `git diff` as possibly stale or truncated (the simulator.py "deletions" and the guard-report "doubled JSON" seen this session were both FUSE illusions; Read-tool views were correct).

## 4. Next-session queue

1. **PART 0 report arrives → audit** (strictly per the S3D spec PART 0 / 12.0 CPU-h gate): projection written BEFORE any certificate/fit/score compute; single-thread accounting; lower-bound basis stated; the 12.0 line unmoved; if the measured lower bound (or the full-projection total) > 12.0 → STOP preserved, and NO cells/members/seeds/budget shrunk to fit; preflight guard re-passes; the emitted BANK-OPS file list == the audited scope (no hidden/extra files); claim ceiling = PART 0 compute-projection only.
2. **Verdict routing**: within 12.0 → do NOT auto-run the full certificate battery; STOP for operator go-ahead first. Exceeds 12.0 → successor spec / operator budget decision (budget line is operator-adjustable with a signed note; evidence thresholds immovable; never cite the S2 24 CPU-h tractability firewall against this budget line).
3. **Bank** (operator, only after audit ACCEPT): Claude emits the filled-in scoped script with `BASE_PIN = 80bfad4` (or the pushed HEAD).
4. **Carried forward from 20260703B (STILL OPEN — read B for detail, not re-derived here):** S4 standing obligations (planted-VALUE leak mutant; `stable_fact` RNG reconciliation; runtime sealing enforcement; per-gap N note; policy-class compute plan); Track-T completion (6 FULL_SCOUT small jsons + L-005 ledger transition; LFS large files already in `2575d1a`); loose ends (AGENTS.md anti-commentary lines; ~13 EOL-churn worktree files — diagnose before ever `git add`; optional checkpoint FROZEN_FILES hardening).

## 5. Evidence-status marks

- S3a / S3b / S3c: banked, pushed, audited (unchanged).
- S3d preflight (guard machinery + partition-order fix): banked `80bfad4`, audited ACCEPT; **PART 0 gate RUNNING**; NO certificate / NULL / gap number exists yet.
- Score exposure to date: chance-level internal-validation figures only; nothing selectable, heldout, or gap-shaped.
