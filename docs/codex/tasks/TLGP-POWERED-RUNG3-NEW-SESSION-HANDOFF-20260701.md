# TLGP Powered rung3 Learner — New Session Handoff (2026-07-01)

## 0. TL;DR (where we are)
Three banks landed this session, each **independently clean-room-verified** (git objects + artifacts + verdict recompute):
- `06307c5` — retrieval fix + rung0 rerun (the pooling-artifact confound that faked "family/learnability-limited" is overturned).
- `7dfb0bde` — powered rung0 **FORMAL terminal** `route_open_capability_witness_feasible` (10/10 seeds; SEEN rules = prerequisite, **NOT transfer**).
- `7f7de677` (**HEAD**) — candidate-free rung3 **IDENTIFIABILITY** probe `rung3_headroom_exists_authorize_powered_learner` (ideal≈0.96 ≫ fair≈0.20, headroom 0.76) ⇒ **rung3 is identifiable; the wall is LEARNABILITY, not identifiability.** (The cheap probe did NOT save the GPU — as predicted, the deterministic linear-mod-K world is over-identified by 24 adapt examples.)

The powered rung3 learner (the REAL transfer test) is **AUTHORIZED** and mid-setup:
- Phase A (freeze + smoke) audited **PASS**; I caught 2 ablation defects: **FIX-1** ablation must run on the **TEST** set, not train; **FIX-2** collapse must be **advantage-destroyed** (`ablated_balacc ≤ fair_max + EPSILON`), not the weak "closer-to-fair".
- Phase B Step-0 re-froze @ canonical `88b9f3af` (FIX-1/FIX-2 + full budget) — I **CLEARED** the freeze-review.
- Full-run launch **STOPPED correctly**: there is **no full-run executor** — the Phase A module is smoke-only and `--full-run` hard-refuses. Codex refused to fabricate an unreviewed executor and launch a 28–82h job. Correct.

> **CURRENT FRONT:** author the full-run executor `rung3_powered_full_run.py` (bound to `88b9f3af`) + a tiny dry-run → STOP for Claude review → pin the executor sha → launch the full run. Ready-to-paste instruction in §6.

> Re-verify every sha/commit/number below against the live repo before acting. That discipline is what has kept this line clean.

## 1. Current repo state
- `D:\Project\AIProject\MyProject\intelligence-theory-lab`, branch `codex/meta-theory-scaffold`, HEAD `7f7de677008b02d257da3a030a7d1e840999072a`, ahead 12 of origin, **never pushed** (remote blocked until `scripts/push.*` hardcoded-PAT is rotated).
- This-session lineage: `9e3e3d2` (session start) → `06307c5` → `7dfb0bde` → `7f7de677` (HEAD).
- **Uncommitted/untracked, intentionally not banked yet** (powered rung3 work in progress):
  - `docs/task_cards/TLGP-CAPABILITY-WITNESS-RUNG3-POWERED-LEARNER-001A.md` (AUTHORIZED; Status line marks two-phase execution)
  - `src/tlgp_capability_witness_preflight_001a/rung3_powered_learner.py` (Phase A **smoke-only**; `--full-run` raises `phase_a_full_run_forbidden`)
  - `src/tlgp_capability_witness_preflight_001a/rung3_single_family_adjudicator.py` (the H0/H1 judge; sha `5773f5d1`)
  - `artifacts/.../RUNG3_POWERED_LEARNER_001A/{SMOKE, PHASE_B_FREEZE_REVIEW, FULL_RUN/failure_manifest.json}`
- Pre-existing untracked noise (ITL-DEV-BENCH runs, LRGG, TLGP-001A-AUDIT, `_writetest`, etc.) is NOT ours — **never `git add -A` / `git add .`; explicit paths only**.
- **Sandbox mount quirks (host git is authoritative):** FUSE staleness (files can read as 0 bytes or stale — host had the real 115-row `val_curves` when sandbox showed 0), `improper chunk offset` warnings on git object reads (results still correct), no-delete mount (`rm` → "Operation not permitted"), stale `.git/index.lock` + `.git/HEAD.lock` need host-side removal before git ops, CRLF/EOL churn is a mount illusion (host is clean). Bank on host with normal git.

## 2. Key anchors (VERIFY before use)
- prereg canonical `6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7` — governs DELTA=0.1 / FLOOR=0.2 / close_fraction_min=9 / N_SEEDS=10 / MODEL_SEEDS `[20260710..20260719]` / rung defs / splits.
- `retrieval_model.py` sha256 `0cba923965f305c6c8cab41a8dd033d7a34bf1c3cd60b0ea27a7fdcc698bf2bb` — validated instrument, READ-ONLY.
- `route_decision.py` `0dcf3659…` — rung0 capability-witness adjudicator (banked); rung3 uses a DIFFERENT judge (below).
- `meta_learners.py` `358d2bb2…` — the confounded mean-pool source; DO NOT edit or use as a primary family.
- `rung3_single_family_adjudicator.py` `5773f5d1` — single-family H0/H1 judge; 8 terminals (integrity → rung0 → rung1 eligibility → discriminativeness/ablation → baseline_saturation → h0/h1), fail-able; **reused unmodified** by the powered rung3 card.
- rung3 probe frozen design canonical `c2a32ed8612d53186dff54245d9c8c8a86abcdc2f020e78dcd2f6910c2b0d706`.
- powered rung3 **Phase B frozen design canonical `88b9f3af0bee52331b9ec6e702349477db48cdd1b244386586f77b5d150664d5`** (CLEARED; full budget 10 seeds; FIX-1 ablation-on-test; FIX-2 advantage-destroyed; EPSILON=0.1=DELTA).
- rung3 graph_cache `rung3_graph_cache_baselines.py` `921d4407` (readback — verify; it is a REAL successor_map, N1 fixed).

## 3. Verified vs claim ceiling
Verified this session (independently): all three banks (exact allowlists, protected shas unchanged, LFS pointers, verdicts recomputed byte-identical from committed inputs, freeze canonical shas recomputed — not self-declared). Powered rung0: both 0a=1.0 & 0b∈[0.914,0.988] ≥0.9 on 10/10; fair_max 0.226 incl no_adaptation + graph_cache; leakage clean planted-caught; overlap 3.97%; power passes. rung3 probe: ideal≈0.96 ≫ fair≈0.20 (incl real graph-cache); headroom 0.7596, LCB 0.7568 ≫ ε; adjudicator self-test all terminals reachable incl the ceiling branch; controls fail-able; replay 2000 records.

Claim ceiling (do NOT exceed): rung0 = SEEN-rule prerequisite (formal), NOT transfer. rung3 probe = candidate-free identifiability only (task is well-posed / solvable-in-principle), proves NOTHING about a learner learning it. Nothing is transfer / mechanism / agency / self / subjectivity / AGI / EGO evidence.

## 4. Immediate queue (in order)
1. **CURRENT FRONT** — author the Phase B full-run executor `rung3_powered_full_run.py` (bound to `88b9f3af`; faithful; reuse validated components; REAL full-budget training) + a tiny NON-evidential dry-run → STOP. Instruction in §6.
2. Claude reviews the executor + dry-run (faithful to `88b9f3af`? real training? correct eval sets? evidence complete? replay reconstructs? no tuning/leakage/banked edits?) → **pin the executor sha** → clear it.
3. Launch the full 10-seed run (~28–82h) → verdict (`h0_amortized` / `h1_headroom_survives` / `baseline_saturation` / `invalid_*`). STOP at verdict; no commit/push.
4. Claude **final re-audit** of `FULL_RUN/` artifacts: recompute the verdict via the unmodified adjudicator `5773f5d1`; confirm the context-ablation actually collapsed on the TEST sets under the advantage-destroyed criterion (the gate that lets H0/H1 be emitted at all); baseline-saturation gate; leakage; replay-from-trace within 1e-9; no banked edits → **bank** (scoped, explicit paths, LFS pointers, no push).

## 5. Standing policy / lessons
- Verify, don't trust readback. Freeze design + record canonical sha BEFORE reading results (anti-tuning). STOP means STOP. Never edit banked/frozen source (new work = new files). Positive control before interpreting negatives. Hairline thresholds → prefer fit-conditioned/substantive reads.
- **NEW this session — freeze ≠ executor.** The code that produces expensive evidence must ALSO be reviewed-before-run (review the executor + a tiny dry-run before the full GPU spend), not just the frozen design.
- **Governance deviation (frozen in `88b9f3af`):** the powered rung3 SUBSTITUTES `retrieval_model` for the prereg's confounded pooling primaries (`in_context_gru`/`in_context_transformer`). Pre-declared, frozen, declared; claim scoped to the SINGLE retrieval family (prereg's two-family H1 clause relaxed to single-family). Do NOT silently reinterpret the prereg; do NOT edit prereg / verdict.py / route_decision.py / the adjudicator.

## 6. Ready-to-use — CURRENT FRONT Codex instruction (author executor + dry-run + STOP)
```
TASK: Author the Phase B FULL-RUN ORCHESTRATION for TLGP-CAPABILITY-WITNESS-RUNG3-POWERED-LEARNER-001A,
then a TINY dry-run, then STOP for review. DO NOT launch the full 10-seed run. The frozen design 88b9f3af
is CLEARED; this task builds the reviewed executor that implements it.

BIND: recompute the Phase B design canonical sha; confirm == 88b9f3af0bee52331b9ec6e702349477db48cdd1b244386586f77b5d150664d5;
if mismatch STOP. Implement the design FAITHFULLY; do NOT change any frozen parameter (budget/seeds/lr/
EPSILON/DELTA/capacity/collapse-criterion/decision-statistic) or the adjudicator.

NEW FILE (executor): src/tlgp_capability_witness_preflight_001a/rung3_powered_full_run.py.
Do NOT edit the Phase A smoke module, the adjudicator (5773f5d1), retrieval_model (0cba9239), or any
banked/frozen source. REUSE read-only the VALIDATED components: context_ablation_report (test-set +
advantage-destroyed), evaluate_fair_panel, ideal_predictions, the leakage scan, splits,
rung3_single_family_adjudicator.compute_verdict, retrieval_model. Write a REAL full-budget training loop
(NOT the tiny smoke trainer).

IMPLEMENT per frozen design 88b9f3af:
- Real training per seed (10 MODEL_SEEDS): train retrieval_model on the rung train split, n_train 5000 /
  n_val 1000, lr-grid {1e-3,3e-4} + val-selection, max_epochs 200, early-stop per prereg; dense val curve.
- STAGE 1 rung1 eligibility: eval seen-disjoint test (n_test 200); pass = meta_balacc >= ideal_seen1 - DELTA
  on >=9/10; rung1_scanner; context-ablation ON RUNG1 TEST (shuffle + no-adapt; advantage-destroyed
  ablated<=fair_max+EPSILON; both modes per seed; aggregate >= close_fraction_min). Gate rung3 on this.
- STAGE 2 rung3 real: train withheld-regime; eval 125 TEST_RULES unseen, query {3,4}; per seed
  ideal/meta/fair(incl real graph_cache)/headroom_vs_meta; context-ablation ON RUNG3 TEST; leakage per rung;
  feed recorded fields to the UNMODIFIED adjudicator → verdict (h0/h1/baseline_saturation/invalid_*).
- STAGE 3 rung2 diagnostic (reuse rung3 model).
- Emit (full contract): result.json, trace.jsonl (LFS), val_curves.jsonl (LFS), replay_report (reconstruct
  verdict from trace within 1e-9), baseline_comparison, ablation_report, eligibility_report, leakage_report,
  route_decision_input, route_decision, manifest (pins: executor sha, adjudicator 5773f5d1, design 88b9f3af,
  prereg sha, capacity, split assertions, GPU env, family-substitution decl). failure_manifest on any stop.

THEN — TINY DRY-RUN (wiring proof, NON-EVIDENTIAL): 1 seed, a handful of episodes, a few hundred steps,
through BOTH stages; confirm end-to-end: training runs; eligibility gate evaluates; context-ablation on TEST
computes the advantage-destroyed collapse; adjudicator emits a verdict; ALL evidence files written; replay
reconstructs the tiny verdict within 1e-9. Emit under FULL_RUN/DRY_RUN/ with dry_run_report.json marked
evidential=false.

STOP for review. Do NOT launch the full 10-seed run. Do NOT commit/push/add audit-review layers/bank
self-rewriting scripts. Report: the new executor path + its sha256, the dry-run report, confirmation the full
run is NOT launched, and confirmation no banked/frozen source or the frozen design changed.
```

## 7. The real open question
The powered rung3 run tests whether `retrieval_model` **amortizes unseen-rule inference**: **H0** (closes to ideal, headroom ≤ DELTA on ≥9/10 = transfer works, bounded capability) vs **H1** (LCB(headroom) > DELTA = within-episode headroom survives, bounded, NOT "recurrence/consciousness required") vs **INVALID** (rung1 not eligible / ablation doesn't collapse / baseline saturation). The identifiability probe already showed the task is solvable in principle, so this is purely the **learnability** question. A large share of probability sits on INVALID; every outcome is bounded and none is mechanism/consciousness evidence.

## 8. Memory pointers
Full running log lives in the assistant's memory: index `MEMORY.md` (the very long "ITL-DEV-BENCH/TLGP CURRENT FRONT" entry) + topic file `itl-devbench-to-tlgp-pivot-and-bank-route-001a.md` §1–8. This handoff is the summary; the topic file has the per-step verification detail.
