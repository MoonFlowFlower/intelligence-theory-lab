# SESSION-HANDOFF-FSP-20260705A

Predecessor: `SESSION-HANDOFF-FSP-20260704C.md` (c0c6bf4 audit + launchpath; battery not yet launched).
Role this session: **independent auditor** (CLAUDE.md "Same-Agent Bridge Audit Role 001"). No
implementation. Operator ran all banks. Date: 2026-07-05. Branch `codex/meta-theory-scaffold`,
HEAD **`5416206`** (ahead of origin by 3 commits; no push performed — operator's call).

---

## TL;DR (state at handoff)

1. **The L=30 S3d battery ran and STOPped** — `STOP_runtime_guard_exceeded_signed_line` at **31.95
   CPU-h**, 41/43 units done, after `ideal::cert::flat_theta`. Clean void STOP, banked `d983b59`.
   No theory evidence — battery `s3d_results_void: true`. "Is the theory correct?" still unanswered.
2. **My prior variance verdict was falsified and I own it.** I judged 22.297 CPU-h "launch-safe";
   the run hit 31.95 (+43%). Root cause = **systematic projection underestimate, not noise**: the
   isolated single-eval-user × N extrapolation under-measured true per-unit batch CPU by **1.71×**
   on the 7 ideal units (21.61 vs projected 12.63) and **1.82×** on the 2 NN units (5.93 vs 3.26).
   `wall_cpu_ratio_flag_count: 0` → this was real CPU, not wall contention. Lesson banked:
   memory `itl-cost-projection-precision-not-accuracy` (cross-sample CV proves precision, not
   accuracy; after the first full run, set the line from **measured** cost, retire the projection).
3. **Path chosen: unit-level resume.** Instead of re-burning ~31 CPU-h, reuse the 41 completed units
   (spot-check–gated) and run only the 2 missing (`discounted_LS_lambda_0.95` cert+NULL). Cards
   drafted, signed, banked (`5416206`).
4. **Governance correction (operator caught a framing issue; I corrected the record):** the signed
   §8 says *"second breach returns to operator"* — there is **no** auto-close / no-third-raise clause
   to override. So continuing is within the signed terms. 002A therefore is a measured line-reset
   **plus a self-imposed hard endgame** (next breach → close, no 002B) that is *stricter* than §8.
5. **Next action = hand the resume Codex prompt (below) to Codex.** Precondition now met (002A signed
   L=38 banked + resume card banked + STOP banked). Codex implements resume, emits bank-ops, STOPs
   for my audit.

---

## 1. Commit lineage / anchors (branch `codex/meta-theory-scaffold`)

- `c0c6bf4` — 001B-IMPL (constant-cell ideal + k*SE guard + canonical scorer). **Audited ACCEPT**
  this-prior-session; oracle-safe, no banked artifact changed, no stop falsely suppressed.
- `2a4502a` — PART-0 CPU-time launch preflight (launchpath slice; audited ACCEPT prior session).
- `a0a211f` — PART-0 CPU-time regate (B1 wall→CPU fix; pushed to origin).
- `d983b59` — **L=30 battery STOP void boundary evidence** (banked this session; 9 files; verified:
  exactly the fresh STOP evidence, no stale report, zero file deletions).
- `5416206` — **banked the 4 cards** (interp pre-reg + 002A signed + resume + checklist). HEAD.

## 2. Banked cards (all under docs/codex/tasks/, all frozen at `5416206`)

- `...-S3D-BATTERY-INTERPRETATION-PREREG-001A.md` — **N1/N2/N3**, signed Leo 26/7/4. Binds the
  *resume-completed* battery audit (still valid pre-reg because the void run produced no adjudicated
  result). N1 = evidence only from committed runner; N2 = constant cells are baseline-saturated
  degenerate controls (ideal 1.0 ties predict_none/majority/global_prior/predict_all) → not
  mechanism evidence; N3 = `rag_should_win_stable_facts` is instrument-fragile (metric swings
  0.0→0.0586→0.1363 by scorer, clears guard by 0.007 on n=79) → weak evidence; mechanism-strength
  claims anchor **only** on camouflage_off / low_diversity / flat_theta.
- `...-S3D-BUDGET-DECISION-002A.md` — signed **[X] reuse-completed, L = 38 CPU-h, Leo, 2026-07-05**.
  Formula: 31.95 measured-exact (41 units + PART0) + ~6 margin for the 2 unmeasured discounted_LS
  units. Endgame §4: **next breach of L=38 → S3d battery CLOSES, no 002B.** (Cosmetic: §6 has a
  doubled "Formula + arithmetic used:" label from a paste — harmless, do not rewrite the banked note.)
- `...-S3D-BATTERY-RESUME-001A.md` — the resume design (DELTAs 1–4 + gates). Read this before auditing.
- `...-S3D-BATTERY-LAUNCH-OPERATOR-CHECKLIST-001A.md` — orchestration checklist.

## 3. IMMEDIATE NEXT ACTION — Codex resume prompt (paste as-is)

```
ROLE: Executor for FSP-PUM-ENV-IDPROBE-001A-S3D-BATTERY-RESUME-001A. Compute + code only.
You run NO git. You change NO science rule. You do not bank.

READ (read-only rule sources — do not modify): the resume card; BUDGET-DECISION-002A (read L=38 from
§6); the interpretation pre-reg card; the exec card; frozen spec 001A/001B.

PRECONDITION (self-check; if unmet write a precondition failure manifest and STOP): 002A §6 signed
(reuse-completed, L=38, operator, date) AND banked; STOP evidence banked; interp pre-reg banked.
Read L from §6; do not set it yourself.

IMPLEMENT (execution-layer only, isolated):
1. Persist each completed unit's FULL result (score_payload incl. per_user_confusion, metric_digest,
   process_cpu_seconds, code_path_hash, input-hash) keyed by unit_id. State whether trace.jsonl
   already carries per_user_confusion (reconstruct from it if so).
2. Skip-completed on resume: reuse a unit iff persisted result exists AND code_path_hash == the
   committed runner hash the void run recorded AND frozen inputs/seeds/frozen_design hash match.
   Reused units add their RECORDED process_cpu_seconds to the runtime-guard cumulative. A partially-
   computed unit re-runs from scratch (no serialized mid-flight state). Derive the 2 missing units
   from the trace (43 expected minus 41 completed) — do NOT hardcode; expect discounted_LS_lambda_0.95
   on flat_theta(cert) + NULL_env(null).
3. Spot-check gate (BLOCKING, must be fail-able): pick 3 completed units at random (seeded, logged),
   recompute bit-exact, compare metric_digest + per_user_confusion sha256 to persisted. ANY mismatch
   -> discard ALL reuse; full re-run under L, or STOP if L cannot cover it. Spot-check recompute CPU
   is verification overhead: disclose separately, DO NOT count it toward L.
4. Before the resume run, preserve the void run's outputs under *_void_line30_v1 names (do not
   overwrite in place).
5. Runtime guard = reused-recorded + newly-executed-measured (contention-robust CPU; wall disclosed);
   STOP at L=38; a breach = battery close per 002A §4 endgame (do NOT auto-raise). threads=1 workers,
   N*1 <= physical cores, GPU prohibited.
6. Analysis-only one-pager s3d_ideal_kernel_analysis_001a.md: does the cert-cell per-cell ideal
   already run through the S2e log-domain kernel? Enable a faster existing path ONLY with a
   byte-identical regression proof (camouflage_off ideal 0.09948462995337995 exact + ideal
   metric_digest unchanged on >=1 cell). If it needs a NEW equivalence certificate, do NOT attempt it.

GATES (all BLOCKING): spot-check bit-exact; reused code_hash+input match; *_v1 preserved; banked
STOP/probe/spec artifacts byte-unchanged; NO science rule touched and NO metric depends on reuse
(assert a resumed unit's metric == its void-run metric bit-exact); py_compile + focused pytest pass;
if the battery completes, cert/null/baseline/ablation/replay freshly written by the committed runner
(N1), consistent with the merged trace.

FORBIDDEN: git; touching frozen spec/thresholds/filter semantics/18-member/cert-cells/strength/k;
mid-computation serialized state; any metric depending on reuse-vs-fresh; banking the void stale
reports as fresh; auto-raising L; a temp/inline report driver.

ON COMPLETION OR STOP: emit an operator bank-ops proposal allowlisting ONLY freshly-changed files
(exclude unchanged tracked files + stale reports; use required-core-subset + zero-deletion +
no-unexpected gate, NOT strict staged==allowlist count), HEAD-pinned, git reset first, per-file
Get-FileHash, scoped commit, no push. Then STOP for Claude audit. Do NOT bank.
Report: verdict; L read; units reused vs re-run (ids); spot-check (3 ids/seeds/digests); total
contention-robust CPU-h (reused+new) + spot-check CPU disclosed separately; wall/CPU flags; per-unit
producer_function = committed runner (N1); _v1 preserved; artifacts written; any STOP fired.
```

## 4. When Codex returns — what THIS auditor must check (audit cycle)

- **Spot-check gate is genuinely fail-able** (not a rubber stamp): confirm the 3 recompute digests
  are compared and a mismatch truly discards reuse. Consider asking for a fault-injection demo.
- **No metric depends on reuse**: a resumed unit's metric must be bit-exact to its void-run value.
- **N1 provenance**: every headline `producer_function` is the committed runner; replay from the
  merged committed trace. Any temp/inline driver number = provenance BLOCKER.
- **Reuse legitimacy**: code_hash + input-hash gating present; `_v1` void evidence preserved; banked
  STOP/probe/spec artifacts byte-unchanged (read committed blobs / host, not the FUSE mount).
- **bank-ops allowlist clean**: only freshly-changed files; no stale reports; no unchanged-file
  zero-stage tripping the gate (the pattern in `s3d_stop_bank_ops_line30_corrected_001a.ps1`).
- **Then apply the interp pre-reg (N1/N2/N3) to any completed battery** — constant cells = controls,
  stable_facts = fragile, strength only on the 3 discriminative cells.
- If the resume battery **completes**: verify cert/null/baseline/replay freshly written + internally
  consistent with the trace; NULL false-headroom check; BASE-invariance; heldout 800–999 untouched.
- If it **STOPs again at L=38**: per 002A §4 endgame, that is **battery close** — do not draft a 002B.

## 5. Standing lessons reinforced this session (for the next auditor)

- **Cost projection: precision ≠ accuracy.** An unvalidated ×N extrapolation on the dominant term is
  an accuracy risk no cross-sample precision can bound. Use measured cost after the first full run.
  The CPU-time **runtime guard** is the real cost control; it behaved exactly as predicted (bounded
  STOP at ~32, ~2 CPU-h overshoot = one in-flight ideal unit, no runaway).
- **FUSE mount truncates freshly-written host files.** `bash` on the mount gave `result.json`
  corrupt at line 190 and `trace.jsonl` as 4 lines / `trace.csv` as 5 rows. The **file-API (Read
  tool)** returned them intact. For committed blobs use `git show <commit>:<path>`; for uncommitted
  fresh host writes use the file-API or host-side. Never trust the mount for provenance.
- **§8 = "second breach returns to operator", not auto-close.** Don't manufacture an override.
- **Stale `.git/index.lock`** blocked the first bank (script failed safe). The rung1-harness
  "protective lock" caveat no longer applies (rung1 done + commits since). Confirm no live git, then
  `Remove-Item .git\index.lock`.

## 6. Open items / debt (isolated from the resume path — do NOT sweep into S3d commits)

- **Repo hygiene debt**: a large untracked set (old TLGP / LRGG / gate4 / dev-bench artifacts, many
  cards + scripts + src/tests) plus ~13 modified files that are EOL/CRLF churn (`AGENTS.md`,
  `decision_log.md`, gate4/ctsr artifacts). Needs its own scoped pass; **never `git add -A`**.
- **Delete** the superseded defective `artifacts/FSP-PUM-ENV-IDPROBE-001A/s3d_operator_bank_ops_proposal_line30.ps1`.
- Two untracked generators (`s3d_part0_stop_report_generator.py`, `s3d_freshness_manifest_generator.py`)
  — decide whether to bank when auditing the resume run (relates to the ephemeral-driver lesson).
- Push: branch is ahead of origin by 3 (d983b59, 5416206, and 2a4502a); operator's call; PAT rotate
  per standing rule if pushed.
- Parked design-only: MPVL/EBPP control baseline + FSP-BORROWED-STACK-REGISTRY (P1); Track-T bank of
  rung1 (H_cap segment-bounded) + ledger L-005 still pending.

## 7. Claim ceiling (this whole session)

Bounded offline audit + boundary evidence only. Established: (a) c0c6bf4 is a faithful oracle-safe
001B instrument impl; (b) the L=30 battery produced a **clean void cost-boundary STOP** at 31.95
CPU-h with a measured projection-bias diagnosis; (c) a signed, endgame-bounded resume path (L=38).
It does **not** establish any S3d certificate/NULL/baseline/ablation/replay result, environment
validity, gap, mechanism, learning, agency, self-awareness, autonomy, EGO/companion readiness, or the
correctness of any theory (Bio-CMBC / CVPSM / VCCO / CMBC / R/G). No valid battery evidence exists yet.
