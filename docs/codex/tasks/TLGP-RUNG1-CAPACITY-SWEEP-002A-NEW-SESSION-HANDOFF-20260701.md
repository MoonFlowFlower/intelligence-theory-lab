# TLGP rung1 Capacity Sweep 002A — New Session Handoff (2026-07-01)

## 0. TL;DR (where we are)
This session took the powered-rung3 line through two clean banked negatives and caught one would-be false
verdict. All commits are local, never pushed.

- `d00932d9` — **rung3 powered full run stopped at stage1_gate**: rung1 seen-rule eligibility failed 0/10
  (meta≈0.52, converged, vs ideal 1.0 / bar 0.9), rung3 correctly gated off. Independently certified a
  **VALID bounded CONFIG-LIMITED negative** (raw-trace recompute 0.504-0.541; not undertraining; leakage
  clean at n=200; ablation real). Banked.
- `b812552a` (**HEAD**) — **rung1 capacity sweep 001A** ran and emitted `route=H_arch`. **I caught it as
  INVALID_optimization_confound and it was NOT accepted.** The larger capacities (C1 512, C2 768) collapsed
  to chance (meta≈0.2025=1/K, loss≈ln5, both lrs, killed by early-stop) — they never trained; C2 fails even
  k=8 that C0 solves. Root cause: `nn.TransformerEncoderLayer` default **Post-LN** needs lr warm-up
  (Xiong 2020, arXiv:2002.04745); fixed lr + no warm-up + early-stop patience 20. Banked as a confound with
  a `CLAUDE_AUDIT_…` note overriding the byte-preserved `result.json` route.

**CURRENT FRONT:** corrective card **002A is AUTHORIZED**. The freeze+dry-run Codex instruction is handed
(reproduced in §6). Awaiting Codex to produce `rung1_capacity_sweep_002a.py` + `FREEZE/design.json` +
tiny dry-run → STOP → Claude review. **The capacity-vs-architecture question is still OPEN** (001A never
tested it fairly because the big models didn't train).

> Re-verify every sha/commit/number below against the live repo before acting. That discipline is what has
> kept this line clean.

## 1. Current repo state
- `D:\Project\AIProject\MyProject\intelligence-theory-lab`, branch `codex/meta-theory-scaffold`,
  HEAD `b812552a6dab645d7bd8df45ffed39d561979140`, ahead 15 of origin, **never pushed**
  (remote blocked until `scripts/push.*` hardcoded-PAT is rotated).
- This-session lineage: `7f7de677` → `cb324b78` (docs: learning-success standard) → `d00932d9`
  (rung1-eligibility negative bank) → `b812552a` (capacity sweep 001A INVALID_confound bank).
- **Untracked, intentionally not banked yet:** `docs/task_cards/TLGP-CAPABILITY-WITNESS-RUNG1-CAPACITY-SWEEP-002A.md`
  (AUTHORIZED). 002A runner + `RUNG1_CAPACITY_SWEEP_002A/` do NOT exist yet (Codex to author).
- Pre-existing untracked noise (ITL-DEV-BENCH, LRGG, TLGP-001B, older handoffs, `_writetest`, etc.) is NOT
  ours — **never `git add -A` / `git add .`; explicit paths only.**
- **Sandbox/FUSE quirks (host git is authoritative):** files read EARLY can be data-cache stale (sandbox
  showed executor `e9c680f4` while host had `a0dcea8d`; use the manifest self-hash + preimage argument, or a
  host `sha256sum`, to pin). Files never read before are fresh (001A runner pinned `863b2b43` from sandbox).
  `git status` shows a huge EOL/CRLF `M` illusion (host clean; `--ignore-all-space` empty). `improper chunk
  offset` warnings on git object reads are cosmetic (data still correct). Bank on host with normal git.

## 2. Key anchors (VERIFY before use — READ-ONLY / frozen)
- prereg canonical `6e61a831c6f287c10c25cccbb09a40671410cd4805214dbd91d62528b2c3d5a7` (DELTA=0.1,
  MODEL_SEEDS [20260710..19], budget).
- `retrieval_model.py` `0cba9239…` — validated instrument, **Post-LN**, capacity via `build_model(params)`
  dict; NEVER edit (capacity stays a clean variable).
- `meta_learners.py` `358d2bb2…` (r2); `route_decision.py` `0dcf3659…`; `rung3_graph_cache_baselines.py`
  `921d4407…` (real successor_map); `rung3_single_family_adjudicator.py` `5773f5d1…`.
- `rung3_powered_full_run.py` `a0dcea8d…` (banked). `rung1_capacity_sweep.py` `863b2b43…` (banked 001A
  runner — may import read-only, do NOT edit).
- Frozen designs: rung3 `88b9f3af…`; sweep-001A `79e51bb4…`; **002A design = TBD (Codex freezes; Claude
  recomputes).**

## 3. Verified vs claim ceiling
Verified this session (independently, from raw artifacts / git objects): both banks clean (message,
exact file set, no forbidden source, LFS pointers, protected shas, parent lineage). rung1 negative real
(trace recompute, converged, leakage-clean n=200). 001A H_arch = optimization confound (C1/C2 chance/loss=lnK
from val_curves; C2 fails k=8 that C0 clears; wider ⊇ narrow expressivity ⇒ optimization not architecture);
C0 reproduced banked 0.52 to ~2e-4.

Claim ceiling (do NOT exceed): two bounded rung1-only negatives at a frozen config; **nothing is transfer /
rung3 / H0 / H1 / mechanism / agency / self / subjectivity / AGI / EGO / mainline evidence.** Capacity-vs-
architecture is UNRESOLVED. Even a clean 002A H_arch means only "architecture-limited over the swept,
*trained* range."

## 4. Immediate queue (in order)
1. **CURRENT FRONT** — Codex authors `rung1_capacity_sweep_002a.py` + freezes `002A design.json` + tiny
   dry-run → STOP. Instruction in §6.
2. Claude review: recompute the 002A canonical design sha (freeze BEFORE results); audit runner
   (AdamW+warm-up+cosine+grad-clip+relaxed-early-stop faithful to the frozen recipe; **trainability control
   trains-and-gates and EXCLUDES untrained caps from the breakpoint**; C0 anchor; eval sets; no frozen-model
   edit; advantage-destroyed ablation on TEST; replay≤1e-9; confirm-token guard; protected intact); set
   `CAP_HOURS` from dry-run timing; **pin runner sha** → CLEAR.
3. Launch full 002A scout (pre-launch verify HEAD/runner-sha/`--validate-only`/git-clean → `--full-run
   --confirm-full-run <002A sha>`) → STOP at route.
4. Claude final audit of the 002A route (trainability-gated; recompute meta from raw val_curves/trace;
   verdict = **H_cap** → reopen powered rung3 / **H_arch_legit** → downgrade OK / **INCONCLUSIVE_optimization**
   → recipe/scale unresolved). Bank accordingly (scoped, LFS, no push; preserve failures byte-as-recorded;
   audit note overrides if confounded).

## 5. Standing policy / lessons
- **Verify, don't trust readback.** Recompute shas and recompute metrics from raw trace/val_curves, not the
  summary.
- **Freeze ≠ executor.** Review the runner + a tiny dry-run before the expensive GPU run; record the canonical
  design sha BEFORE reading results (anti-tuning).
- **NEW this session — capacity/scale sweeps MUST trainability-gate each capacity** before reading a failure
  as architecture-limited. Post-LN transformers collapse to chance without warm-up; a bigger model failing a
  task a smaller one solves = optimization confound, not capacity/architecture. (001A's H_arch was this.)
- **Preserve confounded/failed results byte-as-recorded**; override the interpretation with a banked audit
  note + commit message — do NOT patch `result.json`.
- STOP means STOP. Never edit banked/frozen source (new work = new files). Positive control before
  interpreting negatives. Hairline thresholds → prefer fit-conditioned/substantive reads.

## 6. Ready-to-use — CURRENT FRONT Codex instruction (author 002A runner + freeze + dry-run + STOP)
(Frozen recipe values are pre-declared so they are set before results; Claude recomputes the sha and reviews.)
```
TASK: FREEZE + author the corrected runner + a TINY non-evidential dry-run for
TLGP-CAPABILITY-WITNESS-RUNG1-CAPACITY-SWEEP-002A, then STOP for Claude review. DO NOT launch the full
scout. Card: docs/task_cards/TLGP-CAPABILITY-WITNESS-RUNG1-CAPACITY-SWEEP-002A.md. Repo root, PYTHONPATH=. .

WHY: 001A route H_arch was INVALID — C1/C2 collapsed to chance (loss=lnK, both lrs, killed by early-stop)
because Post-LN needs warm-up and lr wasn't width-scaled. 002A fixes the TRAINING RECIPE ONLY (frozen
retrieval_model architecture NOT edited — capacity stays a clean variable) and adds a per-capacity
trainability control. SCOPE = rung1-only. NOT rung3/transfer/H0/H1. Claim ceiling per card §10.

STEP A — FREEZE canonical design at
artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/RUNG1_CAPACITY_SWEEP_002A/FREEZE/design.json with EXACTLY:
- capacity_grid: C0{256,4,4,4}, C1{512,6,8,4}, C2{768,8,12,4}   (heads | d_model)
- seeds: first 3 prereg MODEL_SEEDS [20260710,20260711,20260712]
- rule_counts (breakpoint map): [8,16,32,64,128,172]; trainability_control_rule_count: 2
- budget inherited from prereg 6e61a831: n_train 5000 / n_val 1000 / n_test 200 / batch_size 256 /
  max_epochs 200 / steps_max 200000
- RECIPE (the fix; frozen):
    optimizer: AdamW, betas [0.9, 0.95], weight_decay 0.1 on 2D weight matrices only
      (no decay on biases / LayerNorm / 1D params), grad_clip_global_norm 1.0
    lr_schedule: linear warm-up for warmup_epochs=15, then cosine decay to min_lr = 0.1 * peak_lr
      over the remaining epochs to max_epochs
    peak_lr_grid (per-capacity, val-selected): [3e-4, 1e-4, 3e-5]
    early_stop: patience 20, but NOT allowed before min_epochs = warmup_epochs + 20 = 35
- clear_threshold: meta >= ideal - DELTA(0.1) on >= 2/3 seeds; EPSILON 0.1
- trainability_control: k=2 must reach meta >= 0.90 on >= 2/3 seeds; FAIL => TRAINABILITY_FAIL = INVALID
    (that capacity is EXCLUDED from the breakpoint map and MUST NOT be read as architecture-limited)
- c0_anchor: C0 must pass trainability AND C0 meta@172 >= banked 0.52 - 0.03 (=0.49); else STOP (recipe harmful)
- decision_rules: H_cap (bp increases across ADMISSIBLE caps) / H_arch_legit (all relevant caps admissible
    AND bp flat/non-increasing) / INCONCLUSIVE_optimization (any larger cap fails trainability even under
    this recipe -> NOT an architecture claim)
- claim_ceiling + full_scout_forbidden_until_review: true + per_cell_wall_clock_cap_hours: null (Claude sets)
Compute + record _frozen_canonical_sha256 (strip underscore keys, canonical JSON sort_keys+compact, sha256 —
same scheme as 001A). Print the recomputed sha.

STEP B — NEW FILE: src/tlgp_capability_witness_preflight_001a/rung1_capacity_sweep_002a.py
- REUSE READ-ONLY (do NOT edit): retrieval_model.build_model(params) [capacity via params; architecture
  UNCHANGED, stays Post-LN], meta_learners build_tensors/eval, world.ideal_predictions/make_episode_for_rule,
  splits, lower_reference + rung3_graph_cache_baselines fair panel, tlgp_001a.leakage. Re-implement FAITHFULLY
  the advantage-destroyed context_ablation (on TEST), replay-from-trace, fair/ideal/leakage per cell, and the
  k-rule subset construction (172 => S.make_episodes("rung1"); k<172 => deterministic TRAIN-pool subsample
  disjoint from TEST). You MAY import these read-only from rung1_capacity_sweep.py (863b2b43) but do NOT edit it.
- NEW training loop: AdamW + param-group weight decay + grad-clip + linear warm-up + cosine decay + relaxed
  early-stop (min_epochs floor). val_curves MUST record per-step lr + a warmup flag (schedule auditable from trace).
- Per-capacity TRAINABILITY control runs FIRST for each capacity (train k=2, gate >= 0.90 on >=2/3). A capacity
  that FAILS is marked TRAINABILITY_FAIL and EXCLUDED from the breakpoint map.
- C0 anchor gate; breakpoint map over admissible caps; trainability-gated decision (H_cap / H_arch_legit /
  INCONCLUSIVE_optimization).
- Guards: --validate-only (design sha + heads|d_model + recipe-params-match-frozen + protected-diff),
  --dry-run, --full-run --confirm-full-run <canonical_sha>. Per-cell full contract (result/trace[LFS]/
  val_curves[LFS]/baseline_comparison/ablation_report/leakage_report/replay_report/manifest); manifest pins
  runner sha, retrieval_model 0cba9239, design canonical sha, prereg 6e61a831, per-cell capacity+
  parameter_count, recipe, GPU env. failure_manifest on any stop.

STEP C — TINY DRY-RUN (wiring proof, NON-EVIDENTIAL): reduced counts (1 capacity, 1 seed, k=2 + one small
cell, few hundred steps) through the trainability-control path + one breakpoint cell; confirm end-to-end:
warm-up schedule computes (lr rises then decays), AdamW+grad-clip step, trainability path evaluates,
ideal/fair/leakage/advantage-destroyed-ablation compute, replay reconstructs within 1e-9, ALL files written.
Emit under RUN/DRY_RUN/ with dry_run_report.json evidential=false. The dry-run must NOT assert the
trainability gate or the C0 anchor (too few steps) — wiring only.

DO NOT edit: retrieval_model.py(0cba9239 — architecture stays Post-LN), meta_learners.py(358d2bb2),
world/splits/preregistration/lower_reference/leakage, rung3_graph_cache_baselines.py(921d4407),
rung3_single_family_adjudicator.py(5773f5d1), rung3_powered_full_run.py(a0dcea8d),
rung1_capacity_sweep.py(863b2b43, banked 001A), any banked artifact, AGENTS.md, CLAUDE.md, any frozen design.json.

STOP for review. Do NOT launch the full scout. Do NOT commit/push/tag/stage/bank/add audit layers/
self-rewriting scripts. Report: runner path + its sha256; the design canonical sha256; the dry-run report;
confirmation the full scout is NOT launched; confirmation no banked/frozen source changed.
```

## 7. The real open question
Does **more capacity of the same Post-LN retrieval_model, trained fairly (warm-up + width-scaled lr, gated on
a per-capacity trainability control), clear rung1 seen-rule eligibility at higher rule counts?** 001A could
not answer it (big models never trained). Outcomes: H_cap (capacity moves the breakpoint → reopen powered
rung3) / H_arch_legit (trained big models still don't → architecture-limited over the trained range, downgrade
OK) / INCONCLUSIVE_optimization (recipe still can't train them → not an architecture claim). All bounded; none
is transfer/mechanism/consciousness evidence.

## 8. Memory pointers
Full running log: assistant memory index `MEMORY.md` (the long "ITL-DEV-BENCH/TLGP CURRENT FRONT" entry) +
topic file `itl-devbench-to-tlgp-pivot-and-bank-route-001a.md` §7-10 (§10 = this bank + the 001A confound +
the trainability-control lesson). This handoff is the summary; the topic file has per-step verification detail.
