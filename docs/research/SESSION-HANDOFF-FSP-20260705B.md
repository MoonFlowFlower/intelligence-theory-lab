# SESSION-HANDOFF-FSP-20260705B

Predecessor: `SESSION-HANDOFF-FSP-20260705A.md` (HEAD `eadcba8`; resume not yet run).
Role this session: **independent auditor** (CLAUDE.md "Same-Agent Bridge Audit Role 001"). No
implementation except drafting the tombstone card. Operator ran all banks + Codex. Date: 2026-07-05.
Branch `codex/meta-theory-scaffold`, HEAD **`5cb9039`** (ahead of origin; no push performed).

---

## TL;DR (state at handoff)

1. **S3d v0 is being TOMBSTONED (route downgrade R3).** After the GRU-seed repair let the battery
   re-run cleanly, it voided on `FAIL_NULL_FALSE_HEADROOM`. Two bounded diagnostics then established
   the instrument is invalid as a latent-mechanism gate on **two independent grounds** (§"Why" below).
   Recommendation accepted: **close v0, do not patch.**
2. **The GRU-seed repair succeeded (real banked win).** GRU-family units are now replay-deterministic
   (Stage 1 A≠B confirmed; Stage 2 determinism + regression gates passed). The 20260705A determinism
   defect is fixed. This did NOT rescue S3d — it let it fail cleanly for a deeper reason.
3. **Tombstone card written but NOT yet executed/committed:**
   `docs/codex/tasks/FSP-PUM-ENV-IDPROBE-001A-S3D-V0-TOMBSTONE-001A.md` (currently **untracked**).
4. **Battery-run-2 (L=38) void evidence is UNCOMMITTED** (Codex emitted bank-ops but did not bank).
   The tombstone Codex prompt commits it as STEP 1.
5. **IMMEDIATE NEXT ACTION:** hand the tombstone Codex prompt (below) to Codex → it commits the void
   evidence, writes `s3d_v0_closure_record.json` (numbers re-derived from committed artifacts),
   self-verifies the decisive claims, commits card + decision_log → STOP for audit → **then operator
   signs `§operator` in the card and banks.**

---

## 1. Commit lineage (branch `codex/meta-theory-scaffold`)

- `eadcba8` — 20260705A handoff (predecessor HEAD).
- `5b9d9bb` — resume STOP `resume_reuse_gate_failed` (spot-check caught GRU nondeterminism). Banked.
- `0316548` — GRU seed determinism repair card, `§7` signed route A (Leo). Banked.
- `273137f` — "Preserve outstanding ITL workspace artifacts and docs" — **broad 162-file sweep** (debt §6).
- `30caa7f` — NULL-env ideal diagnostic 001A → `RESIDUAL_ACTION_STRUCTURE_VIA_STYLEMAP`.
- `5cb9039` — NULL-env ideal diagnostic 002A → `PRIVILEGE_RHO_WIDE`. **HEAD.**
- **Uncommitted:** tombstone card (untracked); battery-run-2 void outputs (`result.json`,
  `failure_manifest.json`, `baseline_comparison.json`, `s3d_certificate_report.json`,
  `s3d_null_env_report.json`, `trace.jsonl`, `s3d_resume_manifest.json`, `*_void*` variants);
  pre-existing unrelated dirty worktree (do NOT sweep).

---

## 2. Why S3d v0 fails — two independent grounds

**Ground 1 — instrument identifiability failure (style_map privilege / ρ conflation).**
- NULL false-headroom: ideal `0.07211` > limit `0.03625` (chance 0.03125 + MDE 0.005); all 18 members
  ~chance.
- Diag 001A `RESIDUAL_ACTION_STRUCTURE_VIA_STYLEMAP` (NOT leakage): history- & posterior-independent
  (0.0); wrong-style_map → chance; analytic `0.0722` ≈ battery `0.0721`. The ideal decodes the
  action-only mode via the per-user `style_map` it is handed (recommend internal center 8 remaps to
  31 distinct surface centers over eval users; pooled scorer ≠ single-mode predictor).
- Diag 002A `PRIVILEGE_RHO_WIDE`: oracle score is style_map-gated in the REAL cells too — wrong-style
  collapses it (`low_diversity` 0.324→0.021, `flat_theta` 0.116→0.029). Oracle is handed each
  eval-user's `style_map`; members (fit 0–639 / eval 640–799, **disjoint**) are not. So ρ = member/ideal
  conflates per-user renderer-permutation recovery with latent decoding.

**Ground 2 — baseline dominance on the pre-registered anchor cells (denominator-free; robust to Ground 1).**
Interp pre-reg (N2/N3) restricts mechanism-strength anchoring to `camouflage_off` / `low_diversity` /
`flat_theta`. Void run-2 raw metrics:
- `low_diversity` (ideal 0.324): lookup control `nearest_neighbor` raw **0.162** BEATS assigned member
  `seq_window` raw **0.075** by **2.2×** (control ρ 0.447 vs member ρ 0.150).
- `flat_theta`: members at chance (`discounted_LS` 0.034, `running_average` 0.032).
- `camouflage_off` (thr 0.8): best `gbt` ρ 0.79 — FAIL.
- Every assigned mechanism member FAILS its cell; only cert "pass" (`rag`/`stable_facts` ρ 0.751) is
  N3-flagged instrument-fragile; constant cells (ρ 1.0) are N2-degenerate.

**Note (rules out the simplest "unfair" excuse):** members DO have fair eval-prefix access (confirmed:
`prefix_symbol_counts`/`rates` features, `seq_full`/`seq_window` history). So the failure is not unfair
access — the mechanism simply does not separate from lookup baselines.

---

## 3. IMMEDIATE NEXT ACTION — tombstone Codex prompt (paste as-is)

```
ROLE: Executor for FSP-PUM-ENV-IDPROBE-001A-S3D-V0-TOMBSTONE-001A.
Documentation + evidence-pinning only. No science change, no re-run, no fix, no reopen.

READ (read-only): the tombstone card; spec 001A §5/§7; interp pre-reg 001A (N2/N3);
diagnostics s3d_null_ideal_diag_001a/ (commit 30caa7f) and s3d_null_ideal_diag_002a/ (5cb9039).

ISOLATION: do NOT modify src/, spec, frozen_design, or ANY banked artifact; no re-run; no patch of
void artifacts. Stage EXPLICIT paths only (never git add -A). Leave pre-existing unrelated dirty
worktree files untouched.

STEP 1 — commit the void battery-run-2 evidence (direct scoped commit; void/negative = lightened).
Confirm via git status which S3d battery outputs are uncommitted; stage ONLY those, all under
artifacts/FSP-PUM-ENV-IDPROBE-001A/ (expected: result.json, failure_manifest.json,
baseline_comparison.json, s3d_certificate_report.json, s3d_null_env_report.json, ablation_report.json,
replay_report.json, trace.jsonl, s3d_resume_manifest.json, *_void*/_v1). git diff --cached
--name-only must show ONLY these + nothing outside that dir. Commit.

STEP 2 — generate artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_v0_closure_record.json by RE-DERIVING
(never hardcoding) from the now-committed baseline_comparison.json + s3d_null_env_report.json:
null_ideal_breach; per discriminative cell (camouflage_off, low_diversity, flat_theta) the assigned
mechanism member metric/rho/passed + best control-baseline metric; explicit low_diversity
nearest_neighbor-vs-seq_window ratio; mechanism_members_failing_cert list; source pins (SHA256 of the
two artifacts + commits 30caa7f, 5cb9039, STEP-1 SHA); verdict "S3D_V0_TOMBSTONED"; claim_ceiling.

STEP 3 — VERIFY (BLOCKING; any fail → STOP + failure_manifest, do NOT commit the card, do NOT edit
the card to match): G-a no assigned mechanism member passed==true on a discriminative cell; G-b
nearest_neighbor raw metric > seq_window raw metric in low_diversity; G-c ideal NULL metric > limit;
G-d every card number matches the re-derived record (report mismatches, don't silently fix).

STEP 4 — append a decision_log.md entry: closure verdict + two grounds + commit pins.

STEP 5 — commit directly (scoped): card + s3d_v0_closure_record.json + decision_log.md entry.
git diff --cached --name-only shows only those three. No push.

REPORT: verdict; re-derived numbers; G-a..G-d; any mismatch; files committed; commit SHA. STOP for
Claude audit. Do NOT reopen S3d v0. Do NOT draft R2.
```

---

## 4. Audit cycle when Codex returns (what the next auditor checks)

- **STEP 1 scoped:** only `artifacts/FSP-PUM-ENV-IDPROBE-001A/` battery files staged; **no unrelated
  dirty files swept in** (the `273137f` lesson).
- **Closure record RE-DERIVED**, not hardcoded; G-a..G-d actually re-read the committed files.
- **Card not edited to match a mismatch** (G-d must report, not silently fix).
- Void evidence preserved, not patched; no src/spec change; FUSE — read committed blobs / file-API,
  not the mount.
- Then **operator signs `§operator` + banks.**

---

## 5. R2 reopen conditions (pre-registered in the card — do not weaken)

A successor `S3d-R2` may open ONLY if it pre-registers, before any number exists:
(1) style-invariant OR equal-access design (ideal infers style_map from prefix; no handed style_map),
used consistently in BOTH the NULL guard AND the ρ denominator (no second ideal / schema fragmentation);
(2) a mandatory falsifier — the mechanism member must **beat (not tie)** the lookup / nearest-neighbor
/ graph-cache / count-table / successor-map family on the discriminative cells, control family reported
alongside; (3) NULL clean for the equal-access ideal. If you cannot say ex ante *why* style-invariant
scoring separates the mechanism from lookup, do not open R2.

---

## 6. Open items / debt

- **`273137f` broad sweep:** 162 files / 260k line-inserts / 0 file deletions; modified some closed-
  lineage banked JSONs (gate4/ctsr, 1-1 churn) + added 5 lines to `AGENTS.md` (operator
  "no optional commentary" instruction). Did NOT touch `src/fsp_pum_env/`, frozen spec, or S3d
  evidence. Non-blocking for S3d; deserves a separate scoped audit that the closed-lineage touches are
  churn-only (hard rule: do not rewrite previous artifacts).
- **Pre-existing unrelated dirty worktree** — never `git add -A`; each pass scoped.
- **Push:** branch ahead of origin; operator's call; PAT rotate if pushed.
- **Parked design-only (carried from 20260705A):** MPVL/EBPP baseline + FSP-BORROWED-STACK-REGISTRY;
  Track-T bank of rung1 (H_cap segment-bounded) + ledger L-005.

---

## 7. Standing lessons this session

- **The scientific-validity gates did their job.** Three consecutive machine STOPs (cost projection →
  determinism → privilege) were the framework catching real defects, not bureaucracy. Keep them.
- **style_map / access-regime is the recurring wall** — same identifiability family as LRGG
  oracle-coupling and equal-access saturation. An ideal-observer handed a per-user nuisance conflates
  nuisance recovery with mechanism.
- **Denominator-free baseline comparison is robust to instrument bugs** — even with ρ contaminated,
  raw-metric `nearest_neighbor > seq_window` closes the mechanism claim.
- **Solo process lightening (adopted this session):** void/diagnostic results commit directly (scoped,
  no HEAD-pin allowlist dance); the executor re-verifies auditor-drafted numbers before committing.
  Reserve heavy ceremony for positive/claim-bearing results.
- **FUSE mount still unreliable** for the git index and fresh host writes; use file-API / `git show`.

---

## 8. Claim ceiling (this session)

Bounded closure + instrument-diagnostic evidence only. Established: (a) the GRU determinism repair
works (units replay-deterministic); (b) S3d v0 is invalid as a latent-mechanism gate on two
independent grounds. Does **NOT** establish any S3d mechanism/cert result, environment validity, or
the correctness/falsity of any theory (Bio-CMBC / CVPSM / VCCO / CMBC / R-G). **Tombstones the v0
instrument, not the research route.** "Is the theory right" remains unanswered.
