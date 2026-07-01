# TLGP-CAPABILITY-WITNESS-RUNG0-RETRIEVAL-RERUN-001A

> Status: DRAFT implementation card. Runs the REAL TLGP rung0 with the validated
> retrieval model — the FIRST interpretable capability-witness experiment (the
> instrument is now repaired). Frozen design: `…RUNG0-RETRIEVAL-RERUN-001A.frozen_design.json`,
> canonical sha256 `e917ad29cc00cb8e48740883a10596829cec52cc2b10032698cf1c2adc61b9af`.
> Model: `retrieval_model.py` (validated `runner_ok` on frozen positive control `90f2a503…`).

Task id: TLGP-CAPABILITY-WITNESS-RUNG0-RETRIEVAL-RERUN-001A

Problem definition: train the validated retrieval model on the REAL TLGP rung0 (seen
8 rules, full value coverage) and measure 0a (train fit) + 0b (in-distribution
held-out). The prior rung0 negatives (pooling metas ~0.37–0.55 on 0b) were CONFOUNDED
by the mean-pool bottleneck; with a model that can attend to per-example adapt tokens,
this is the first un-confounded read of whether the rung0 capability witness is
attainable.

Why it matters: either the witness is now attainable (→ reopen the route: powered run,
then rung1/rung3) or it is a REAL, un-confounded negative (→ clean close of the rung0
witness as a genuine learnability limit). Both outcomes are interpretable — that's the
whole point of having fixed the instrument first.

Honest caveat (in the card): PC_COPY proved RETRIEVAL (answer in context); rung0 0b
requires INFERENCE (infer which of 8 seen rules from 24 adapt examples and generalize
to query cells NOT in adapt). Retrieval-capable ≠ inference-capable; do not assume a pass.

Layer: candidate-free capability-witness probe with a validated instrument. Trend probe
(3 seeds, underpowered); `route_decision.py` returns inconclusive_underpowered by design;
the signal is the 0b trend.

Build instructions: add a NEW runner (e.g.
`src/tlgp_capability_witness_preflight_001a/rung0_retrieval_rerun.py`) that imports the
retrieval model + the TLGP rung0 data construction (R0_RULES, full value coverage via
the world helpers / splits) + `_eval_checkpoint` READ-ONLY, and trains/evals. Do NOT
edit `retrieval_model.py` (post-bank), `meta_learners.py`, `positive_control.py`,
`grokking_probe.py`, `route_decision.py`, the world, or any `src/tlgp_001b_r2/*` /
`src/tlgp_001a/*` byte. If reuse needs editing a banked file, STOP and report.

Frozen parameters (see frozen_design.json — do NOT change after results): retrieval
model (d_model 256, layers 4, heads 4); rung0 = R0_RULES(8), adapt+query full [0..4],
n_train 5000 / n_heldout 200; AdamW lr 3e-4 wd 0.1, batch 256, ≤50k steps, checkpoint
2k; seeds [20260710,20260711,20260712]. Record ideal_balacc + the fair baselines
(lookup/count_table/predict_all/majority) for context.

Pre-frozen, FIT-CONDITIONED go/no-go (FITTED seed = 0a train ≥ 0.95):
- witness_trend_pass → ESCALATE: among FITTED seeds, 0b heldout ≥ 0.80 on ≥ 2/3 seeds →
  the witness looks attainable → draft a powered 10-seed rung0 run (route_decision.py
  for the formal terminal), then rung1. REOPENS the route.
- witness_trend_fail → CLOSE: all FITTED seeds plateau 0b ≤ 0.65 (no material gain over
  the confounded pooling metas) → REAL un-confounded negative → close/downgrade the rung0
  witness as a genuine learnability limit.
- ambiguous → 0b between 0.65 and 0.80, or no seed fits 0a → report curves, operator decides.

Required outputs under
`artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/RUNG0_RETRIEVAL_RERUN_001A/`:
`training_records.json`, `val_curves.jsonl` (dense per-checkpoint 0a train + 0b heldout
per seed), `rerun_report.json` (per-seed 0a/0b + ideal + fair baselines + the go/no-go
verdict), `route_decision_input.json` + `route_decision.json` (UNMODIFIED route_decision.py;
expect inconclusive_underpowered), `manifest.json` (rerun_frozen_design_sha256 = e917ad29…,
positive_control_design_sha256 = 90f2a503…, prereg_sha256 = 6e61a831…,
retrieval_model_sha256, route_decision_sha256 = 0dcf3659…, git HEAD/branch, GPU env,
banked_source_diff_empty), `failure_manifest.json` if a stop fires.

Acceptance gate: 3 seeds complete; dense 0a/0b curves logged; ideal + fair baselines
recorded; fit-conditioned go/no-go applied as frozen; `route_decision.py` run unmodified;
banked source unedited (shas match); capacity unchanged.

Claim ceiling: first interpretable bounded rung0 result with a validated instrument. A
pass authorizes only a powered run (not transfer/H1). A fail is a real un-confounded
rung0 negative, bounded to this world+arch+budget. Proves nothing about rung3/transfer,
mechanism, agency, self, subjectivity, AGI, or EGO.

Process discipline: emit artifacts, STOP at the verdict. Do NOT commit, do NOT add
audit/closeout/review layers, do NOT push, do NOT start a powered run from this card.

Stop conditions → failure_manifest.json: editing any banked file; capacity changed;
go/no-go tuned after results; adding audit layers; committing/pushing; starting a powered
run from this card.

Rollback: new runner file + new artifact dir only; revert = delete them.

Forbidden: editing banked source/world/retrieval_model/meta_learners/positive_control/
grokking_probe/route_decision; capacity change; `AGENTS.md`/`CLAUDE.md`/global config;
`scripts/push.*`; remote/push; extra audit layers.

Auto-Remote-Anchor: forbidden.

Expected cost: 3 retrieval-model rung0 trainings (≤50k steps) — about a day of GPU.

## For Codex (execution)
Run on a GPU machine. Read this card + frozen_design.json + the retrieval-runner card
first. Build `rung0_retrieval_rerun.py` (import retrieval_model + rung0 data construction
+ _eval_checkpoint READ-ONLY), train/eval the REAL rung0 (R0_RULES, full coverage) for 3
seeds ≤50k steps checkpoint 2k, emit the artifacts above (dense 0a/0b curves + ideal +
fair baselines), run the UNMODIFIED route_decision.py, apply the FROZEN fit-conditioned
go/no-go, and STOP at the verdict. Do NOT commit, no audit layers, no push, no powered
run. Final report: per-seed 0a(train) + 0b(heldout best) + ideal + fair-baseline max;
go/no-go verdict; manifest sha matches (e917ad29 / 90f2a503 / 6e61a831 / 0dcf3659);
confirm no banked-source edit, capacity unchanged, nothing committed/pushed. Paste back
for my closing verification.

## Collision Record
Approach A — close the rung0 witness on the prior (confounded) negatives: rejected — they
used a pooling arch that fails the copy positive control.
Approach B — re-run rung0 with the validated retrieval model, pre-frozen go/no-go (this
card): selected — the first interpretable read.
Approach C — jump to powered 10-seed / rung3 immediately: rejected — gate on this 3-seed
trend first.
Selected approach: Approach B.
