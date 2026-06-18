# GROUNDING-GATE — CO-BINDING IDENTIFIABILITY PROBE (GG-COBIND-ID-001A)

Status: **bounded task card + executed.** User authorized this specific check (chose "draft a
bounded card, then run the cheapest candidate-free identifiability check"). Authorization covers
ONLY: write isolated code under the new paths below, run it locally, emit artifacts. It does NOT
authorize a candidate mechanism, schema change, EGO/LLM/AIRI contact, or any
`commit`/`push`/`tag`/`anchor`.

## task id
GG-COBIND-ID-001A

## research layer
Engineering implementation + mechanism hypothesis. NOT subjectivity / consciousness / agency.

## problem definition
Isolate and test the **K2 blocker** from `GROUNDING-GATE-K1-K2-PREFLIGHT-FEASIBILITY-001A.md`:
is "do(L=v) → all three channels (prediction/report/action) change coherently" **identifiable as
evidence of a SHARED latent**, or is it **reproduced by INDEPENDENT per-channel regressors** that
have no shared latent? Minimal linear-Gaussian world. **Candidate-free**: builds only a generator
+ two fair baselines (independent ridge heads; a shared rank-1 score model) + controls. It does
NOT build the proposed grounding-gate mechanism.

Out of scope (deliberately): K1 obs-decodability, history-integration, discrete-report, non-LLM
report. K1 is already deemed answerable (memo §2); this probe isolates K2 only.

## current stage
Pre-implementation card → executed under the single authorization above.

## hypothesis (pre-registered, fail-able both directions)
- **H_close (expected):** independent full-capacity per-channel ridge reproduces the qualitative
  interventional co-change, AND on balanced+ample data shows held-out parity with (or superiority
  to) the shared rank-1 model within `DELTA_R2`. Any shared-model advantage appears ONLY under
  channel-imbalanced data → that is **multi-task transfer**, not self-state co-binding.
- **H_headroom (surprising, admissible):** on balanced+ample data the shared rank-1 model strictly
  beats independent heads by `DELTA_R2` on held-out (independent CANNOT reproduce). This would
  warrant drafting the *reframed transfer* card and NOTHING else.

## baseline (verdict decided against this)
**Independent per-channel ridge** (λ selected per channel on a validation split) — the fair model
that needs NO shared latent. This is the K4-correct competent challenger (regularized, not a naive
overfitting OLS that is trivially beatable).

## candidate-analog (NOT the proposed mechanism)
**Shared rank-1 score model:** estimate one shared direction `u` in L-space from the data-richest
channel; predict every channel as `a_k · (L·u)`. This is the literal "one latent score co-binds all
channels" hypothesis, in its most favorable (linear) form.

## ablation / controls (gate validity)
- **positive_control** (sensitivity): true rank-1 + extreme imbalance → shared MUST beat independent
  on data-poor channels in ≥ `consistency_min` seeds, else `check_underpowered_invalid`.
- **negative_control** (specificity): disjoint-driver generator (no shared score) + imbalance →
  shared MUST NOT beat independent in ≥ `consistency_min` seeds, else `check_invalid_false_transfer`.
- **regime ablation:** balanced_ample vs imbalanced.

## primary metric (frozen)
Held-out **signal R²** (vs the noise-free channel signal, model-independent) on a fixed 2000-sample
held-out set; per channel. Separation = `shared_r2 − independent_r2`. `band = DELTA_R2` (fixed
pre-run, not derived from results). Access parity: identical X (=L), identical held-out, identical
λ grid for both models; the only difference is the model class (logged).

## frozen numeric constants (committed before run; immutable)
`d_L=6, n_channels=3, rank_hypothesis=1, n_ample=400, n_poor=15, n_poor_pc=8, n_heldout=2000,
noise_sd=0.3, ridge_lambda_grid=[1e-3,1e-2,1e-1,1,10], seeds=range(10), DELTA_R2=0.05,
consistency_min=8, eval_target=noise_free_signal`. Hashed into `result.json.prereg_sha256`.

## verdict set (computed from artifacts; fail-able)
- `check_underpowered_invalid` — positive control not detected (STOP).
- `check_invalid_false_transfer` — negative control false-positive (STOP).
- `co_binding_non_identifiable__only_transfer_headroom` — independent reproduces on balanced
  ample; shared wins ONLY under imbalance (transfer, sub-subjectivity). **Self-state route stays
  closed.**
- `co_binding_non_identifiable__no_headroom` — independent reproduces everywhere; even transfer
  absent. **Route fully closes.**
- `headroom_co_binding_identifiable_surprising` — shared beats independent on balanced ample data
  (independent cannot reproduce). Surprising; would warrant ONLY the reframed transfer card.

## trace / replay requirement
`trace.csv`: one row per (regime, seed, channel) with n_train, independent_r2, shared_r2, delta.
Verdict recomputed by `replay_from_trace(trace.csv)` using the same logic — no hidden state, no
future info. `replay_report.json` records match.

## anti-hardcoding audit (checked before AND after)
- [ ] metric on noise-free signal / ground truth, never on a model's own outputs
- [ ] `DELTA_R2` fixed pre-run; not tuned to results
- [ ] positive control fail-able (can flip to `check_underpowered_invalid`)
- [ ] negative control fail-able (can flip to `check_invalid_false_transfer`)
- [ ] independent baseline is a competent regularized fit (not a crippled stub)
- [ ] access parity (same X/held-out/λ-grid; model-class difference logged)
- [ ] multi-seed (10) with ≥8/10 consistency for any "wins" claim
- [ ] verdict computed by boolean logic over the trace, not a report-header literal
- [ ] deterministic seeds → replayable

## stop conditions
positive control undetected → `check_underpowered_invalid`, STOP. negative control false-positive →
`check_invalid_false_transfer`, STOP. secret in run path → BLOCK (no run/commit). All non-blocking
verdicts still produce full artifacts.

## claim ceiling
A result is a **bounded statement about LINEAR interventional co-binding identifiability in ONE toy
world**. It does NOT prove non-identifiability for nonlinear mechanisms; it does NOT evidence self,
agency, emotion, autonomy, subjectivity, or companion-readiness; it informs the grounding-gate
gate-to-draft decision ONLY.

## rollback
Delete `src/gg_cobind_id_001a/`, `tests/test_gg_cobind_id_001a.py`, `artifacts/GG-COBIND-ID-001A/`.
No edits to existing src/contracts/schemas/prior artifacts/push scripts. No git ops.

## pre-implementation plan
- files expected to change (all NEW): `src/gg_cobind_id_001a/{__init__.py,probe.py}`,
  `tests/test_gg_cobind_id_001a.py`, `artifacts/GG-COBIND-ID-001A/*`
- files forbidden to change: everything else
- commands: `python -m gg_cobind_id_001a.probe <artifacts_dir>`; `pytest tests/test_gg_cobind_id_001a.py`
- expected artifacts: result.json, trace.csv, baseline_comparison.json, ablation_report.json,
  positive_control_report.json, replay_report.json, claim_ceiling.txt, failure_manifest.json (if stop)
- rollback: delete the three new paths

## what this does NOT prove
Not self, agency, emotion, autonomy, subjectivity, companion-readiness. Not non-identifiability for
nonlinear mechanisms. Not that the grounding gate is impossible in every world. Only: in the
canonical LINEAR case, whether qualitative interventional co-change discriminates "shared latent"
from "independent heads," and whether any shared-model advantage is confined to data-imbalance
transfer.
