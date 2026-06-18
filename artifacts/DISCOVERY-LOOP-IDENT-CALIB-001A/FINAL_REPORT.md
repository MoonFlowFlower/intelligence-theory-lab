# Final Report — DISCOVERY-LOOP-IDENT-CALIB-001A

Meta-experiment: run the lab's discovery/falsification loop in synthetic, ground-truth-KNOWN
binary-sequence worlds and test whether it is calibrated for **observational** identifiability —
does it separate a latent mechanism from the strongest observation-only baseline when the latent is
genuinely necessary, and report equivalence when it is redundant?

> **Self-authored + self-executed by Claude in one session at the operator's explicit instruction.**
> Per the lab's Same-Agent Bridge Audit Role this conclusion needs an independent hostile audit
> before it is used to reroute lab strategy. Pre-registration was frozen before any result was seen.

## Verdict

`loop_misses_identifiable_latent` (pre-registered, frozen absolute-ε rule).

Plain statement: the loop is **specific but power-limited**. It never false-separates (clean on the
redundant and the no-structure worlds), and it does separate a strong latent world (positive
control), but it **misses a moderate latent world whose true latent advantage (~0.007 nats/symbol)
sits below its detection floor at 3000 training symbols** — reporting "equivalent" even though a
latent mechanism is genuinely necessary there (we built it).

## Research layer
engineering_implementation + mechanism_hypothesis (tool calibration / diagnostic). Not subjectivity,
not consciousness.

## Files changed (all new, additive)
- `src/discovery_loop_ident_calib_001a/__init__.py`, `…/probe.py`
- `tests/test_discovery_loop_ident_calib_001a.py`
- `docs/task_cards/DISCOVERY-LOOP-IDENTIFIABILITY-CALIBRATION-001A.md`
- `artifacts/DISCOVERY-LOOP-IDENT-CALIB-001A/*`
No existing file modified; no global config; no remote push.

## Commands run
- compile + smoke (`run_cell` on 2 worlds + leak probe)
- full 40-cell run via a checkpointed driver (sandbox 45 s/call limit → resumable chunks)
- `pytest tests/test_discovery_loop_ident_calib_001a.py` → **8 passed**

## Provenance
- `prereg_sha256 = c501ac8b464cc8fe…a76d99a`
- `code_path_hash = 2932e3ba5bb86975…65b8afa4` (execution copy)
- `secret_scan.clean = true`
- **Caveat (FUSE):** the sandbox read-mount null-pads/caps `probe.py` to 21503 bytes; the execution
  copy was null-stripped (recovering the true 20274-byte source) before running. The canonical repo
  source is the same content (padding is a read-side artifact). An independent auditor should
  recompute `code_path_hash` from the canonical file via a non-FUSE path.

## Results (per world; 10 seeds each, ε = 0.01 nats/symbol, consistency_min = 8)

| world (truth) | gap_mean | gap range | separates (frozen) | equivalent | sig_pos | world verdict |
|---|---|---|---|---|---|---|
| latent_necessary (2-state HMM, p=.95, e=.8/.2) | +0.0069 | [+0.0009, +0.0124] | 1/10 | 9/10 | 6/10 | **equivalent** |
| latent_redundant (order-1 chain) | −0.0008 | [−0.0047, +0.0002] | 0/10 | 10/10 | 0/10 | equivalent ✓ |
| positive_control (HMM, p=.97, e=.75/.25) | +0.0125 | [+0.0069, +0.0173] | 8/10 | 2/10 | 9/10 | **separates** ✓ |
| negative_control (i.i.d. Bernoulli .5) | −0.0001 | [−0.0006, +0.0000] | 0/10 | 10/10 | 0/10 | equivalent ✓ |

Mechanism-under-test = EM HMM (latent predictor). Baseline = strongest held-out order-k count table
(best k, pro-baseline). In `latent_necessary` the HMM's advantage is **real and consistently
positive** (10/10 positive gaps, 6/10 significant) but small — only 1/10 seeds clears ε.

## Baseline results
The observation-only count table is the strongest simpler alternative and was given its best-case
edge (min held-out loss over k∈{0..4}). It exactly matches truth in `latent_redundant` (best k=1) and
`negative_control` (k≈0), and captures most of `latent_necessary` via k=4, leaving only a ~0.007-nat
residual for the latent model. So `latent_necessary` is a near-baseline-capturable world — the
latent footprint that survives a feasible-order count table is small.

## Ablation results
- positive_control (sensitivity): **passed** — loop separates a guaranteed-identifiable world.
- negative_control (specificity): **passed** — loop does NOT separate a no-structure world.
- leakage probe (test): oracle leak (`hmm_losses(leak=True)`) flips negative_control to
  `separates` (gap +0.6931) → would drive `check_invalid_false_separation`; proves the harness can
  detect future/label leakage. Shipped run uses no leak.

## Replay result
`replay_verdict == result_verdict` (True). Per-step spot-check (seed-0 gaps recomputed from
`trace.jsonl` vs `trace.csv`) reconciles for all 4 worlds. No `failure_manifest.json` (valid run).

## Tests run
8 passed: determinism (generator + cell), causality (flipping a future obs leaves earlier per-step
losses identical), leakage-probe reachability, separation band sourced from PREREG (not a hidden
constant), label-blind fit/score signatures, verdict gates fail-able both directions, and
artifact-backed specificity + replay.

## Anti-hardcoding self-audit
- if-else-as-mechanism: no (EM-HMM + count tables; verdict computed from held-out losses).
- classifier behind math / hidden rule: no (predictive likelihood; generators disclosed, never
  passed to the models — `test_label_blind_signatures` passes).
- threshold tuning after results: **no** — ε=0.01, seeds, world params frozen in PREREG (sha
  recorded) before the run and NOT changed after. `latent_necessary` failing the band is reported
  as-is. The bootstrap **significance view is explicitly labeled EXPLORATORY / non-pre-registered**;
  it was added after a 2-cell smoke and does NOT alter the frozen verdict. This is the one spot an
  auditor should scrutinize; full disclosure given.
- test-only logic path: the `leak` flag defaults off in the shipped run and only the tests set it;
  documented, not a hidden verdict path.
- future obs during prediction: no (causal forward filter / past-only contexts;
  `test_causal_no_future_dependence` passes).
- weak-distribution pass: guarded — the positive control *requires* separation (passed) and the
  substantive miss is a genuine power finding, not a vacuous distribution.
- replayable from trace: yes.

## Interpretation for the user's (a) vs (b) question
Original framing: is the lab's streak of "baseline-equivalence / collapse" verdicts (a) candidates
merely wrong, or (b) targets non-identifiable?

This experiment does **not** cleanly confirm (b). It surfaces a third, more consequential reading
about the **method**:

- The loop's **separation** verdicts are trustworthy (specificity is clean: it never false-separates
  across the redundant and i.i.d. worlds; it does separate a strong latent world).
- The loop's **equivalence** verdicts are **power-limited**. We built a world where a latent
  mechanism is genuinely necessary (it always beats the baseline) and the loop still reported
  "equivalent," because the effect (~0.007 nats at 3000 symbols) sits below its detection floor
  (~0.01 nats here). So a "collapse to baseline" verdict conflates **(a) truly equivalent** with
  **(c) a real mechanism with a small observational footprint** — it cannot, by itself, distinguish
  them, and it is *not* evidence for (b) non-identifiability.

Actionable consequence: every negative/collapse verdict in the lab should carry a **power statement**
— the minimum effect size it could have detected at its data budget. A negative without that is
ambiguous between (a) and (c). This is the empirical instance of the identifiability/power limit:
the loop is a falsifier whose negatives have bounded power, so a streak of negatives is weak
evidence that "the structure is not there."

## Stop conditions triggered
None forced a halt. Run is valid (positive control separated; negative control did not;
replay+spot-check matched; secret clean), so the substantive verdict
`loop_misses_identifiable_latent` stands rather than a `check_*` invalidation.

## Claim ceiling
Bounded calibration of the discovery loop's OBSERVATIONAL identifiability discrimination on 4
synthetic ground-truth-known binary-sequence worlds at L_train=3000. The detection floor (~0.01
nats/symbol) is specific to this alphabet, model pair, and data budget.

## What this does not prove
- Not consciousness / subjective experience / emotion / autonomy / agency / self-awareness / AGI /
  companion-readiness.
- Not interventional (do-calculus) identifiability — this is observational only (the K2 family is
  untouched).
- Not that any specific past lab target was underpowered or non-identifiable (each needs its own
  power analysis).
- Not non-identifiability (b) — the loop demonstrably identifies when the effect is large enough.
- Not a general bound; larger data / different baselines move the floor.

## Remaining unknowns
- The per-result detectable-effect-size (power) of the lab's existing negative verdicts.
- Whether the same power-limitation holds under interventional data (K2) — likely worse, separate test.
- Where exactly the floor sits as a function of L_train (a power curve was not measured here).
