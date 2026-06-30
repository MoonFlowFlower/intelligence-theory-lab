# TLGP-CAPABILITY-WITNESS-GROKKING-PROBE-001B

> Status: DRAFT implementation card. Authorizes the LAST cheap learnability probe on
> GPU — the fit+regularization "Goldilocks" band. NOT a full/powered sweep.
> Follows `…GROKKING-PROBE-001A` (verdict ambiguous-by-label; fitting regime showed
> no grokking). Frozen design: `…GROKKING-PROBE-001B.frozen_design.json`, canonical
> sha256 `515a415b7e2ae41f51d703c131b73927edcacbf92f8e32d34e1cfb815e117e55`.
> Adjudicator (reused, unmodified): `route_decision.py` sha256 `0dcf3659…`.
> Runner (reused, unmodified): `grokking_probe.py` (run with new wd params; NO code edit).

Task id: TLGP-CAPABILITY-WITNESS-GROKKING-PROBE-001B

Problem definition: 001A bracketed but did not test the fit+regularization band:
wd=0.1 fit (train→1.0) but showed NO grokking (heldout flat ~0.55–0.59 over 34k
post-fit steps); wd=1.0 over-regularized and never fit (train<0.95). Test the same
frozen transformer 256/4 on rung0 with weight_decay ∈ {0.3, 0.5} (the only band where
the model may BOTH fit AND be regularized — classically where grokking, if any,
appears), early-stop OFF, lr 3e-4, 50k steps, dense val curves. This is the LAST
cheap single-config learnability probe: it escalates or closes the route.

Spec-fix vs 001A (important): 001A's `grok_negative` required "ALL runs train≥0.95 ∧
heldout≤0.60", which wd=1.0 (no fit) made unsatisfiable → spec-artifact "ambiguous".
001B conditions the verdict ONLY on cells that actually FIT (train≥0.95). A wd that
never fits is recorded uninformative, not blocking. So 001B resolves cleanly.

Layer: candidate-free feasibility preflight; capacity FROZEN; training-regime band
only; NOT a TLGP-R2 run; no H0/H1.

Honest prior (stated, not biasing the frozen gate): given 001A wd=0.1 fully fit then
ran flat, I expect 001B most likely confirms `grok_negative`. The fit+reg band is the
genuine untested spot, so this last check is legitimate; in-context per-episode rule
inference is not classic grokking — do not over-read either way.

Build: NO new code. Reuse `src/tlgp_capability_witness_preflight_001a/grokking_probe.py`
unchanged, invoked with weight_decay {0.3, 0.5}. Do NOT edit grokking_probe.py,
minimal_probe.py, route_decision.py, or any `src/tlgp_001b_r2/*` / `src/tlgp_001a/*`
byte. If grokking_probe.py is not cleanly parameterizable by wd without an edit, STOP
and report (do not edit a banked file).

Frozen parameters (see frozen_design.json — do NOT change after results): transformer
256/4 (frozen); rung0 only; early-stop OFF; AdamW; wd ∈ {0.3, 0.5}; lr 3e-4; batch
256; max_steps 50000 (extension to 100000 only if a fitted cell is trending-uncrossed
AND operator authorizes); seeds [20260710, 20260711, 20260712]; checkpoint every 2000
steps logging {step, train_balacc, heldout_balacc}.

Pre-frozen, FIT-CONDITIONED go/no-go (gates spend/lean only):
- FITTED cells = (seed,wd) with train_balacc ≥ 0.95 at any checkpoint.
- grok_positive → escalate (draft powered 10-seed sweep): among FITTED cells, best
  heldout ≥ 0.75 by max_steps, OR sustained late rise (heldout +≥0.15 over ≥3
  consecutive checkpoints after first train≥0.95).
- grok_negative_close → close/downgrade the cheap learnability route as
  family/capacity-limited for this witness: ≥1 FITTED cell exists AND every FITTED
  cell plateaus (heldout ≤ 0.60, no sustained late rise).
- no_fitting_regime_uninformative: no wd in {0.3,0.5} reaches train≥0.95 → report;
  operator decides (do NOT auto-close).

Required outputs under `artifacts/TLGP-CAPABILITY-WITNESS-PREFLIGHT-001A/GROKKING_PROBE_001B/`:
`training_records.json`, `val_curves.jsonl` (dense per-checkpoint train+heldout),
`probe_trend_report.json` (fitted-cell analysis + go/no-go verdict + numbers),
`route_decision_input.json`, `route_decision.json` (unmodified route_decision.py;
expect inconclusive_underpowered), `leakage_report.json` (clean + planted caught),
`manifest.json` (frozen_design_sha256 = 515a415b…, route_decision_sha256 = 0dcf3659…,
prereg_sha256 = 6e61a831…, grokking_probe_sha256 recorded, git HEAD/branch, GPU env,
capacity_unchanged, banked_source_diff_empty), `failure_manifest.json` if a stop fires.

Acceptance gate: 6 runs (3 seeds × wd{0.3,0.5}) complete or budget_capped; dense val
curves logged; fit-conditioned go/no-go applied as frozen; route_decision.py + grokking_probe.py
unmodified (shas match); leakage clean + fail-able; capacity unchanged; NO banked
source byte edited; manifest shas match; no push.

Claim ceiling: bounded trend/lean on the fit+reg band only. Closes/escalates the CHEAP
learnability route for the transformer-256/4 rung0 witness. Proves nothing about
transfer/rung3/H1, mechanism, capability-witness feasibility as a formal terminal, the
GRU witness, agency, self, subjectivity, AGI, or EGO.

Stop conditions → failure_manifest.json: capacity changed; go/no-go tuned after
results; leakage; any banked TLGP-R2/TLGP-001A/probe-code byte edited; frozen design
edited after results; auto-extend beyond 50000 without operator OK.

Rollback: new artifact dir only (+ no new code if grokking_probe.py is reused). Revert
= delete the GROKKING_PROBE_001B dir. No banked file touched.

Forbidden: editing grokking_probe.py / minimal_probe.py / route_decision.py /
`src/tlgp_001b_r2/*` / `src/tlgp_001a/*`; enlarging capacity; new candidate;
`AGENTS.md`/`CLAUDE.md`/global config; `scripts/push.*`; remote/push.

Auto-Remote-Anchor: forbidden.

Expected cost: ~6 transformer-256/4 rung0 trainings to ~50k steps — ~a day of GPU.
This is the LAST authorized single-config cheap probe; whichever way it resolves, the
cheap learnability route is then escalated or closed.

## For Codex (execution)
Run on a GPU machine. Read this card + frozen_design.json first. Invoke the UNMODIFIED
`grokking_probe.py` with wd {0.3, 0.5} (transformer 256/4 frozen, rung0, early-stop
OFF, lr 3e-4, 50k steps, checkpoint every 2k). Emit the artifacts above (dense val
curves mandatory), run the unmodified `route_decision.py`, compute the FIT-CONDITIONED
go/no-go, and STOP at the verdict — do not start a powered sweep. Final report:
go/no-go verdict; per-(seed,wd) final train/heldout + first step train hit 0.95 +
whether any late heldout rise appeared in fitted cells; manifest sha matches; confirm
no banked-source/probe-code edit, capacity unchanged, no push. Paste back for closing
verification.

## Collision Record
Approach A — close the learnability route on 001A alone: rejected by operator — the
fit+reg band (wd 0.3–0.5) was untested.
Approach B — reuse grokking_probe.py with wd {0.3,0.5}, fit-conditioned verdict (this
card): selected — decisive last cheap check, no new code.
Approach C — powered 10-seed sweep now: rejected — gate it on this probe.
Selected approach: Approach B.
