# TLGP-CAPABILITY-WITNESS-GROKKING-PROBE-001A

> Status: DRAFT implementation card. Authorizes a BOUNDED long-horizon/regularized
> ("grokking-regime") probe on GPU — NOT the full sweep. Sibling of
> `TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A` (Card 2); explicitly EXTENDS its scope
> from "epochs-only budget" to "training regime" (no early-stop + weight decay +
> extended steps), capacity still frozen.
> Frozen design: `…GROKKING-PROBE-001A.frozen_design.json`, canonical sha256
> `93bae0c65171e35e06e2e3ca858026f623be585ae0d3873b1e253ce8b7604be6`.
> Adjudicator (reused, unmodified): `src/tlgp_capability_witness_preflight_001a/route_decision.py`
> sha256 `0dcf3659df802912ff2f760e9875526887e14c4c14d1e0cc91c0cb4d8863c0c8`.

Task id: TLGP-CAPABILITY-WITNESS-GROKKING-PROBE-001A

Problem definition: the minimal probe returned `trend_flat` and was read as
family/capacity-limited — but it inherited a grokking-HOSTILE regime (early-stop
fired at ~290 epochs ≈ ~6k optimization steps; no weight decay). In-context
per-episode modular-rule inference is known to be step/regularization-hungry, and
delayed generalization (if it occurs) appears AFTER the early-stop window. This
probe removes that confound: train the SAME frozen transformer 256/4 on rung0 with
early-stopping DISABLED, weight decay {0.1, 1.0} (AdamW), lr 3e-4, to
max_steps 50000 (≈8× the minimal probe), logging a DENSE train+heldout curve, then
apply the pre-frozen go/no-go.

Why it matters: it converts an over-stated "family-limited" lean into a clean
decision — either rung0 heldout rises (capability becomes plausible → escalate to a
powered sweep) or it stays flat with train fitted (→ honest family/capacity-limited
downgrade, training regime ruled out).

Layer: mechanism-route feasibility preflight, candidate-free. The transformer is the
prereg meta family (NOT a new candidate). The ONLY relaxation vs TLGP-R2 is the
TRAINING REGIME at frozen capacity. Makes NO TLGP-R2 H0/H1 claim.

Build instructions: add a NEW `src/tlgp_capability_witness_preflight_001a/grokking_probe.py`
that IMPORTS the minimal-probe training/eval core and the TLGP-R2 world/rung0/learner
READ-ONLY, and overrides ONLY: early_stopping=off, optimizer=AdamW, weight_decay,
max_steps, dense checkpoint logging. Do NOT edit `minimal_probe.py`, `route_decision.py`,
or any `src/tlgp_001b_r2/*` / `src/tlgp_001a/*` byte. Reuse, do not re-implement, the
model and metric.

Frozen parameters (see frozen_design.json — do NOT change after results):
- capacity FROZEN: transformer d_model 256, layers 4, heads 4, ff_mult 4
- regime: early_stopping DISABLED; AdamW; weight_decay ∈ {0.1, 1.0}; lr 3e-4; batch 256; max_steps 50000 (extension to 100000 only if trending-uncrossed AND operator authorizes — never auto)
- rung0 only; seeds [20260710, 20260711, 20260712]
- checkpoint every 2000 steps, log {step, train_balacc, heldout_balacc}

Pre-frozen go/no-go (gates SPEND/lean only — NOT a scientific terminal):
- grok_positive → escalate (draft powered 10-seed sweep card): best (seed,wd) rung0
  heldout ≥ 0.75 by max_steps, OR delayed-generalization signature (heldout rises
  ≥ +0.15 sustained over ≥3 consecutive checkpoints AFTER train_balacc first ≥ 0.95).
- grok_negative_family_limited → downgrade: train_balacc ≥ 0.95 (fit) but heldout
  stays ≤ 0.60 with NO sustained late rise through max_steps, across all runs.
- ambiguous → report curves + numbers, escalate to operator.

Required outputs under `artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/GROKKING_PROBE_001A/`:
- `training_records.json` — per (seed, wd): final train/heldout, steps_run, budget_capped flag.
- `val_curves.jsonl` — dense per-checkpoint {seed, wd, step, train_balacc, heldout_balacc} (the decisive observable).
- `probe_trend_report.json` — per-run + best, the delayed-generalization signature test, and the go/no-go verdict {grok_positive | grok_negative_family_limited | ambiguous} with numbers.
- `route_decision_input.json` + `route_decision.json` — recorded dict + output of the UNMODIFIED `route_decision.py` (EXPECTED `inconclusive_underpowered`; confirms wiring/fail-able, not the signal).
- `leakage_report.json` — frozen 001A dual-target MI detector, clean + planted controls caught.
- `manifest.json` — frozen_design_sha256 (= 93bae0c6…), route_decision_sha256 (= 0dcf3659…), prereg_sha256 (= 6e61a831…), git HEAD/branch, GPU env, capacity_unchanged, banked_source_diff_empty.
- `failure_manifest.json` if any stop fires.

Acceptance gate: 6 runs (3 seeds × 2 wd) complete or recorded budget_capped; dense
val curves logged; go/no-go applied as frozen; route_decision.py run unmodified (sha
matches); leakage clean + fail-able; capacity unchanged (256/4 only); NO banked
source byte edited; manifest shas match frozen values; no push.

Claim ceiling: bounded trend/lean on the training-regime lever only. grok_positive
unlocks only drafting a powered sweep; grok_negative is a lean (underpowered, 1
config, GRU witness untested). Proves nothing about transfer/rung3/H1, mechanism,
capability-witness feasibility as a formal terminal, agency, self, subjectivity,
AGI, or EGO. Honest caveat: in-context per-episode rule inference is not classic
single-table grokking; delayed generalization may not apply — do not over-read
either outcome.

Stop conditions → `failure_manifest.json`, do not proceed: capacity changed;
go/no-go tuned after results; leakage; any banked TLGP-R2/TLGP-001A byte edited;
frozen_design or route_decision sha mismatch; auto-extending steps beyond 50000
without operator authorization.

Rollback: new file `grokking_probe.py` + new artifact dir only; revert = delete them
(keep minimal_probe.py / route_decision.py). No banked file touched.

Forbidden: editing `minimal_probe.py` / `route_decision.py` / `src/tlgp_001b_r2/*` /
`src/tlgp_001a/*`; enlarging the capacity grid; new candidate mechanism;
`AGENTS.md`/`CLAUDE.md`/global config; `scripts/push.*`; remote/push.

Auto-Remote-Anchor: forbidden.

Expected cost: ~6 transformer-256/4 rung0 trainings to ~50k steps (~8× a minimal
probe cell) — roughly a day of GPU; far cheaper than the full sweep, and decisive on
the regime confound.

## For Codex (execution)
Run in the repo on a GPU machine. Read this card + `frozen_design.json` + the Card 2
design first. Build the read-only `grokking_probe.py`, run the 6-cell regime probe on
rung0 (transformer 256/4, capacity frozen, early-stop OFF, wd {0.1,1.0}, lr 3e-4, 50k
steps, checkpoint every 2k), emit the artifacts above (DENSE val curves are
mandatory), run the unmodified `route_decision.py` on `route_decision_input.json`,
compute `probe_trend_report.json` against the FROZEN go/no-go, and STOP at the
go/no-go — do not start any full/powered sweep. Final report: go/no-go verdict +
per-(seed,wd) final train/heldout + whether any late heldout rise appeared (with the
checkpoint where train first hit 0.95) + manifest sha matches (frozen_design
93bae0c6…, route_decision 0dcf3659…, prereg 6e61a831…) + confirm no banked-source
edit, capacity unchanged, no push.

## Collision Record
Approach A — declare family-limited from the minimal probe alone: rejected — that
conclusion is confounded by early-stop@~6k steps (grokking-hostile).
Approach B — long-horizon/regularized regime probe (this card), capacity frozen,
pre-frozen go/no-go, reusing the probe core read-only: selected.
Approach C — jump to a powered 10-seed grokking sweep now: rejected — expensive; gate
it on this 6-cell probe first.
Selected approach: Approach B.
