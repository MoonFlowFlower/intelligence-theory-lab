# TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A-MINIMAL-PROBE-001A

> Status: DRAFT implementation card. Authorizes a BOUNDED minimal GPU probe ONLY —
> NOT the full sweep. This is the "separate authorized card" Card 2 R1 (C5) required.
> Governing design: `docs/task_cards/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A.md`.
> Frozen pre-commitment: `…preflight_plan.FROZEN.json`, canonical sha256
> `0dd63b6323594a0597133d7460b7816b751f6efc0ee5b250fb79c2f2830f63a7`.
> Adjudicator: `src/tlgp_capability_witness_preflight_001a/route_decision.py`,
> sha256 `0dcf3659df802912ff2f760e9875526887e14c4c14d1e0cc91c0cb4d8863c0c8`.

Task id: TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A-MINIMAL-PROBE-001A

Problem definition: run the pre-declared minimal probe — `in_context_transformer`
(d_model 256, layers 4; the prereg saturation witness, capacity FROZEN), rung0 only,
seeds [20260710, 20260711, 20260712], budget grid max_epochs {200, 600, 800} /
steps_max {200000, 600000, 800000} / lr {0.001, 0.0003} — to measure the
budget→rung0-heldout trend, then apply the FROZEN go/no-go. This GATES (does not
run) the full sweep.

Why: Phase 0 (zero-cost readback of the banked R2 run) found the rung0 floor failure
looks budget-bound — 125/140 rung0 runs hit the 200-epoch cap with train_balacc only
~0.66–0.71 (not converged), ideal=1.0, fair baselines weak (~0.32, no ceiling). The
probe tests whether more budget at the same frozen capacity lifts rung0 heldout
toward the 0.9 bar.

Layer: mechanism-route feasibility preflight, candidate-free. The transformer is the
prereg's own meta family (NOT a new candidate mechanism); the ONLY relaxation vs
TLGP-R2 is TRAINING BUDGET at frozen capacity. This makes NO TLGP-R2 H0/H1 claim.

Build instructions: implement a thin probe runner under
`src/tlgp_capability_witness_preflight_001a/` that IMPORTS the banked TLGP-R2 world /
rung0 data construction / transformer learner READ-ONLY (no edit to any
`src/tlgp_001b_r2/*` or `src/tlgp_001a/*` byte) and overrides ONLY the training
budget. Reuse the existing training/eval code; do not re-implement the model or the
metric.

Pre-declared go/no-go (FROZEN in the plan — do NOT tune after seeing results):
- trend_positive → authorize full sweep: mean(best heldout over 3 seeds) at 800 epochs
  ≥ 0.75 AND (800ep mean − 200ep mean) ≥ +0.10.
- trend_flat → downgrade family-limited: (800ep mean − 200ep mean) < +0.05 AND 800ep
  mean ≤ ~0.664 (no material gain over R2).
- ambiguous → report numbers, escalate to operator; do NOT auto-authorize full sweep.
These gate SPEND only; they are NOT a scientific route terminal.

Required outputs under `artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/MINIMAL_PROBE_001A/`:
- `training_records.json` — per seed×budget×lr: epochs_run, steps_run, train_balacc,
  heldout_balacc, per-epoch val curve, val_still_improving_at_stop.
- `probe_trend_report.json` — 200/600/800-epoch heldout means, deltas, and the
  go/no-go verdict {trend_positive | trend_flat | ambiguous} with the numbers.
- `route_decision_input.json` — the recorded dict in `route_decision.py`'s schema
  (rung0; ideal_balacc; fair_baseline_balacc incl graph_cache+lookup+count_table+
  predict_all+majority; learner_per_seed_balacc; n_seeds=3; leakage_clean).
- `route_decision.json` — output of running `route_decision.py route_decision_input.json`
  (EXPECTED: `inconclusive_underpowered`, because n_seeds=3 < N_SEEDS=10; this is by
  design and confirms the adjudicator is wired and fail-able — the SIGNAL is the
  trend report, not this terminal).
- `leakage_report.json` — frozen 001A dual-target MI detector on every meta input
  channel; must be clean.
- `manifest.json` — frozen_plan_sha256 (must equal 0dd63b63…), route_decision_sha256
  (must equal 0dcf3659…), prereg_sha256 (6e61a831…), git HEAD, GPU/env readback.
- `failure_manifest.json` if any stop fires.

Acceptance gate: all 18 runs (3 seeds × 3 budgets × 2 lr) complete or are recorded
as failed; per-epoch val curves recorded; trend report computed against the FROZEN
go/no-go; `route_decision.py` run unmodified (sha matches); leakage clean; capacity
grid unchanged (transformer 256/4 only); NO `src/tlgp_001b_r2/*` or `src/tlgp_001a/*`
byte edited; manifest shas match the frozen values; no push.

Claim ceiling: spend-gating trend evidence only. Proves NOTHING about
capability-witness feasibility (that needs the full 10-seed sweep), transfer
(rung3/H1), mechanism, learning, agency, self, subjectivity, AGI, or EGO. A
trend_positive only authorizes drafting the full-sweep card.

Stop conditions → write `failure_manifest.json`, do not proceed: capacity grid
changed/enlarged; go/no-go thresholds edited after results; frozen_plan or
route_decision sha mismatch; leakage detected; any banked TLGP-R2 source byte
edited; attempt to run the full sweep from this card.

Rollback: new module + new artifact dir only; revert = delete
`src/tlgp_capability_witness_preflight_001a/` probe runner files (keep
route_decision.py) and the MINIMAL_PROBE_001A artifact dir. No banked file touched.

Forbidden: editing `src/tlgp_001b_r2/*` or `src/tlgp_001a/*`; enlarging the capacity
grid; introducing a new candidate mechanism; touching `AGENTS.md`/`CLAUDE.md`/global
config; `scripts/push.*`; any remote/push.

Auto-Remote-Anchor: forbidden.

Expected cost: ~18 transformer-256/4 rung0 trainings (up to 800 epochs) — hours to ~a
day of GPU, far cheaper than the full multi-config/10-seed sweep this gates.

## For Codex (execution)
Run in the repo on a GPU machine. Read this card and the governing design card first.
Build the read-only probe runner, run the 18-cell budget grid for rung0 with the
transformer 256/4 (capacity frozen), emit the artifacts above, run the unmodified
`route_decision.py` on `route_decision_input.json`, compute `probe_trend_report.json`
against the FROZEN go/no-go, and STOP at the go/no-go — do NOT start the full sweep.
Final report: trend verdict + the 200/600/800 heldout means + per-seed numbers +
manifest sha matches (frozen_plan 0dd63b63…, route_decision 0dcf3659…, prereg
6e61a831…) + confirmation that no banked source byte was edited, capacity unchanged,
and no push.

## Collision Record
Approach A — run the full sweep now: rejected (expensive; the cheap probe gates it).
Approach B — minimal transformer-256/4 rung0 budget probe gating the full sweep:
selected.
Approach C — declare route_open/closed from the probe: rejected (probe is underpowered
by design; only the full 10-seed sweep + route_decision.py yields a scientific terminal).
Selected approach: Approach B.
