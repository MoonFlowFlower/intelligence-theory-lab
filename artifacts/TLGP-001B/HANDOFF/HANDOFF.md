# TLGP-001B — Execution Handoff (run the FROZEN budget on a capable machine)

This package lets a capable machine execute the **full frozen TLGP-001B budget** and emit the
computed verdict. The harness, all guards, and a non-evidential smoke were implemented and the
smoke validated **in a sandbox that cannot run the training budget** (2 CPUs, 45s/call cap,
background processes killed cross-call). Nothing in the frozen prereg was changed.

## 0. Frozen prereg (do not modify)
- `artifacts/TLGP-001B/prereg.json`
- canonical sha256 (json.dumps sort_keys,separators=(',',':'),ensure_ascii):
  `c9f4ba279b75cfc1753a6c6586f11708a9d561bbbff82e8db98859165c580d41`
- raw-bytes sha256: `35e7ade902d6f8bc3b7c8051370b8da874f4a73f3279a606b90e5ee267e9e502`
- `src/tlgp_001b/preregistration.py` recomputes the canonical sha at load and RAISES on mismatch
  (the harness will refuse to run an unverified spec). This is the prereg pin.

## 1. Environment
```
pip install -r artifacts/TLGP-001B/HANDOFF/requirements.txt
# torch: CUDA build strongly recommended (see requirements.txt)
```
Validated: numpy 2.2.6, scikit-learn 1.7.2, torch 2.12.1.

## 2. Verify source provenance BEFORE running
```
python - <<'PY'
import hashlib, json
man = json.load(open("artifacts/TLGP-001B/HANDOFF/source_manifest.json"))
for rel, want in man["delivered_src_tlgp_001b"].items():
    got = hashlib.sha256(open(rel,"rb").read()).hexdigest()
    assert got == want, f"SOURCE DRIFT {rel}: {got} != {want}"
print("source_manifest OK; delivered == on-disk")
PY
```
FUSE caveat: do NOT run from a FUSE-mounted path that serves stale `.pyc`. Run from a normal
checkout, and `find src -name __pycache__ -type d -exec rm -rf {} +` first.

## 3. Run the full frozen budget
```
cd <repo-root>
find src -name __pycache__ -type d -exec rm -rf {} +
PYTHONPATH=. python -m src.tlgp_001b.harness --full
```
This trains the pre-registered meta panel (in_context_gru / in_context_transformer /
amortized_summary_mlp) at the per-family **saturation witness** (largest frozen capacity) across
the 10 frozen MODEL_SEEDS and both lrs, under four data conditions (REAL_withheld,
CAPACITY_CONTROL, context-ablation, shuffle), then computes ideal/lower-reference scores,
leakage controls, exact replay, tamper fail-ability, provenance, and the **computed verdict**.

The verdict precedence keys ONLY on the largest capacity of every family (saturation logic), so a
witness-based run is decision-correct under the frozen precedence. (Optional corroboration: the
full capacity sweep is available via `meta_learners.capacity_configs()`; it is NOT required by the
frozen verdict precedence.)

## 4. Expected compute (measured on this 2-CPU sandbox; scale to your hardware)
Per single training (batch 256, 5000 train episodes):
| family witness | s/epoch (2 CPU) | ~s @ 60-epoch early-stop |
|---|---|---|
| in_context_gru (h256,l2) | 3.62 | ~217 |
| in_context_transformer (d256,l4) | 17.26 | ~1035 |
| amortized_summary_mlp ([256,256]) | 0.39 | ~23 |

`--full` trains **80 runs/family** (10 seeds x 2 lr x {REAL, CONTROL, context-ablation, shuffle}),
240 total. On 2 CPUs that is ~28h (60-epoch early stop) to ~82h (200-epoch cap), Transformer-
dominated. On a CUDA GPU these are tiny nets: expect far less.

## 5. Decision statistic (frozen)
- metric: mean over test episodes of per-episode **balanced accuracy** on held-out queries.
- `headroom_vs_meta = ideal_mean - meta_mean`; `ideal` = 001A in-family Bayesian observer (probe
  ceiling, excluded from the fair panel).
- `LCB = mean(headroom_vs_meta) - 2*std/sqrt(N_SEEDS)`, N_SEEDS=10.
- DELTA=0.10, FLOOR=0.20.
- capacity control: CAPACITY_CONTROL-regime headroom must close (`<= DELTA`) on **>= 9/10 seeds**
  per family, else INVALID (meta underpowered).

## 6. Verdict enum (computed, frozen precedence)
1. **INVALID** `tlgp001b_invalid_capacity_or_leakage_or_replay` — iff capacity-control fails to
   close >=9/10 for any family, OR any planted leak uncaught, OR any clean channel falsely flagged,
   OR replay not exact.
2. **H1 (BANK)** `tlgp001b_within_episode_headroom_survives_meta` — iff for the largest capacity of
   EVERY family: `LCB(headroom_vs_meta) > DELTA` AND context-ablation collapses (meta <= FLOOR+DELTA)
   AND shuffle collapses (meta headroom <= DELTA).
3. **H0 (DOWNGRADE)** `tlgp001b_headroom_amortized_by_meta__downgrade_001a` — otherwise.

## 7. Artifacts produced by `--full` (under artifacts/TLGP-001B/)
`result.json` (verdict + prereg pin + per-seed + LCB + power statement + tamper + source hashes),
`baseline_comparison.json`, `ablation_report.json`, `replay_report.json`,
`positive_control_report.json`, `failure_manifest.json`, `claim_ceiling.txt`.

## 8. Acceptance-signal checklist (where each appears in result.json)
- frozen prereg sha readback -> `prereg_pin_sha256` / `prereg_pin_match`
- delivered==executed source hashes -> `source_hashes_delivered_equals_executed` (+ HANDOFF/source_manifest.json)
- per-seed meta results -> `headroom_vs_meta_per_seed`
- capacity-control >=9/10 -> `capacity_control_closed_seeds` (+ verdict_detail.capacity_control_ok_per_family)
- LCB = mean - 2*SE -> `witness_lcb_headroom_vs_meta`
- headroom_vs_meta -> `witness_lcb_headroom_vs_meta` + per-seed
- context ablation -> `context_ablation_meta` (+ ablation_report.json)
- shuffle ablation -> `shuffle_headroom` (+ ablation_report.json)
- leakage planted/clean -> `leakage` (+ positive_control_report.json)
- replay exact -> `replay.replay_exact` (+ replay_report.json)
- tamper failability -> `tamper_failability` (5 axes; each flips the computed verdict)
- exact final verdict enum -> `verdict`
- claim ceiling -> `claim_ceiling` (+ claim_ceiling.txt)
- forbidden-path readback / no-git -> the harness writes ONLY under artifacts/TLGP-001B/ and runs
  NO git op; verify with `git status` after the run.

## 9. Anti-tamper / governance
Do NOT change thresholds, capacity grid, seeds, splits, or training budget (any such change is a
forbidden post-hoc mutation -> the run is INVALID and is governance self-modification). The harness
performs NO git operation. Any remote anchor is operator-initiated only, scoped explicit `git add`
(NEVER `git add -A`, NEVER scripts/push.*). This run is drafter-implemented and must be independently
audited before its verdict is banked.

## 10. Claim ceiling
Bounded offline evidence on whether ONE procedural world's within-episode inference headroom
survives cross-episode amortization by THIS meta family at this frozen capacity grid. Candidate-
free; tests NO mechanism. NOT learning-as-mechanism, agency, self, feeling, subjectivity,
intelligence, or EGO-readiness evidence.
