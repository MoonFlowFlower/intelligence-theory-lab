# PREREG FREEZE — UNCERTAINTY-VOI-REQUEST-MECHANISM-003A (intelligence-theory-lab)

> Ex-ante pre-registration, **successor to 002A**. Repo: **intelligence-theory-lab** (NOT Ego). 002A (R3 `e54e8e2b`) was ruled `ATTRIBUTION_FAILURE` by the frozen rule, but Claude's Yellow audit found the verdict is **not supported by the data and is reversed**: the mechanism beats both rivals (~27%) and its advantage is DESTROYED / driven strongly negative by every falsifier and the key ablation (wrong_sign A≈−123, shuffled ≈−67, uncertainty_ablation ≈−17, value_ablation ≈0) — a strong VOI-attribution signature. The `ATTRIBUTION_FAILURE` label was an artifact of a **mis-specified G2/G3**: 002A required the falsified advantage's CI to *include 0* (collapse-to-parity) and thus mislabeled the stronger collapse-to-negative as "survival." This prereg corrects G2/G3 to the mechanistically-correct attribution signature. 002A/001A artifacts are preserved (no-delete); this file does not edit them. All values below are **frozen at the commit that banks this file**, which MUST be an ancestor of the 003A implementation and of any gated run it judges. **No post-hoc tuning.**

## Anti-tuning declaration (Red change, flagged ex-ante)
The G2/G3 correction is a **logic fix**, not a threshold tuned to observed numbers. Justification is magnitude-free and independent of the 002A values: a genuine feedback-dependent advantage must be *removed* by corrupting the feedback (it may land at parity OR go negative — both are collapse); only a feedback-**independent** advantage (e.g. a cost-savings artifact) would remain significantly positive. Safeguards: (1) this correction is pre-registered ex-ante of a **fresh** scored/transfer seed block (9401–9430) that did NOT motivate the correction; (2) a pre-freeze simulation confirmed the corrected gate *discriminates* — it passes the feedback-dependent advantage and would fail a cost-only artifact; (3) it does NOT re-score 002A's frozen artifacts; (4) any positive verdict still requires a full Claude hostile audit. q (process-noise) is **kept at 0.004** and NOT tuned for calibration — the pre-freeze sim showed lowering q to improve calibration destroys the advantage; therefore calibration (G4a) is expected to fail and the expected outcome is `VOI_MECHANISM_PRESENT_UNCALIBRATED`.

## Layer / claim ceiling (binding)
Layer 3 mechanism hypothesis. **Claim ceiling:** bounded offline evidence that ONE implemented uncertainty/value-of-information mechanism (myopic knowledge-gradient with exploit pressure), in ONE toy environment, beats BOTH a best-tuned static-threshold rival AND a random-active baseline on a hold-and-observe VOI task, AND that this advantage is attributable (collapses to ≤ parity under wrong-sign feedback, shuffled feedback, and uncertainty-ablation), with held-out generalization. Proves NO general intelligence, real-world adaptation, world-modeling, understanding, self/agency/autonomy, subjectivity, emotion, consciousness, EGO/companion readiness, and specifically NOT that the pet has this mechanism. Calibration of the uncertainty estimate is a SEPARATE sub-claim (G4a); an `UNCALIBRATED` pass drops it. A PASS = a mechanism-proxy for uncertainty-driven VOI decision-making in a bounded toy.

## Environment (frozen — UNCHANGED from 002A/001A)
- `K = 8` arms, horizon `H = 200`. `v_i(t+1) = clip(v_i(t) + N(0, τ_i²), 0, 1)`, 4 fast `τ_hi = 0.06`, 4 slow `τ_lo = 0.005` (fixed per episode from env-seed), `v_i(0) ~ U(0,1)`. `σ_obs = 0.10`, `c_q = 0.02`, `c_r = 0.08` (request → lower-noise `σ_obs/3` on top-2 by μ). Env-seed fixes trajectories + noise (paired).

## Task / reward / regret model (frozen — UNCHANGED from 002A: MODEL A hold-and-observe)
- Each step the agent auto-holds `inc(t) = argmax_i μ_i(t)` and realizes `v_{inc(t)}(t)`; selects one info action ∈ {noop (cost 0), query(i) (cost c_q), request (cost c_r)}. `regret_t = (max_j v_j(t) − v_{inc(t)}(t)) + cost(a_t)`. Cumulative regret over H, lower better, paired. oracle: `inc = argmax v`, regret 0.

## Mechanism under test (frozen — UNCHANGED from 002A)
- Belief Kalman `(μ_i, σ_i²)`, `σ_i² += q` between steps, **`q = 0.004`** (single constant; NOT tuned; agent does not know per-arm τ). Update `K=σ_i²/(σ_i²+σ_n²)`, `μ_i += K(x−μ_i)`, `σ_i² *= (1−K)`, `σ_n = σ_obs` (query) / `σ_obs/3` (request).
- KG (exploit pressure): `σ̃_i = σ_i²/sqrt(σ_i²+σ_n²)`, `Δ_i = μ_i − max_{j≠i} μ_j`, `KG(query i) = σ̃_i·f(−|Δ_i|/σ̃_i)`, `f(z)=φ(z)+z·Φ(z)`; `KG(request) = Σ_{top2 by μ} σ̃_i·f(−|Δ_i|/σ̃_i)` at `σ_n=σ_obs/3`. `a* = argmax[KG−cost]`; if `max[KG−cost] ≤ 0 → noop`. value_ablation: `KG(query i)=σ̃_i`.

## Baselines, controls, floors, ceiling (frozen — UNCHANGED from 002A)
- RIVALS (beat BOTH by MDE): `static_threshold` (tuned θ/period on 9301–9310 only), `random_active` (query uniform-random arm each step).
- CONTROLS: `wrong_sign` (`x'=2μ_i−x`), `shuffled` (per-episode permuted pool), `uncertainty_ablation` (σ frozen constant), `value_ablation` (KG=σ̃, ignore Δ).
- FLOORS (non-learning): `hold_only`, `no_update`. CEILING: `oracle` (regret 0).

## Seeds (frozen; assert pairwise disjoint; fail closed) — **FRESH scored/transfer vs 002A**
- Probe `9001`. Tuning `9301–9310` (θ/period only). **Scored (primary verdict basis) `M = 20`, `9401–9420` (fresh; not used to motivate the G2/G3 correction).** **Held-out transfer `9421–9430`.** Optional secondary replication `9101–9120` from 002A may be reported but is NON-gating. Single seeded agent RNG stream; no unseeded RNG.

## Metrics + gates (thresholds frozen)
Per rival R: paired advantage `A_R = regret(R) − regret(mechanism-variant)` per seed. Mean, 95% bootstrap paired CI, effect size over M=20. **MDE: relative advantage ≥ 10%.**
- **G1 rival-beat (both required):** `G1a` mean `A_static > 0`, CI excludes 0, rel ≥ 10%; `G1b` same vs `random_active`.
- **G2 falsifiers (CORRECTED attribution signature):** define "advantage collapses under control C" := `A_C` 95% CI **upper bound ≤ 0** (falsified mechanism NOT significantly better than the rivals) **AND** `A_clean − A_C` 95% CI **lower bound > 0** (drop is significant). **G2 passes iff the advantage collapses under BOTH `wrong_sign` AND `shuffled`.** (Collapse accepts parity OR negative; a feedback-independent advantage that stays significantly positive FAILS.)
- **G3 ablations (CORRECTED):** `uncertainty_ablation` must **collapse** (defined as in G2). `value_ablation` must be **load-bearing** := `A_clean − A_value_ablation` 95% CI lower bound > 0. **G3 passes iff uncertainty_ablation collapses AND value_ablation is load-bearing.**
- **G4a calibration** (frozen tolerance): `z_i(t) = (μ_i(t) − v_i(t))/σ_i(t)` (offline diagnostic; ground truth for scoring only, not fed to the model). Pass iff `mean(z²) ∈ [0.7, 1.5]`. Report 90%-coverage fraction. (Expected to FAIL given q=0.004; see anti-tuning declaration.)
- **G4b transfer:** advantage vs the better rival on held-out seeds `A_transfer` CI excludes 0.
- **G5 replay:** fresh-process ×2 bit-exact; AST rng-audit + fail-able positive control; gate-scoped trace + `metric_records` ≤ 25 MiB.
- **G6 floor dominance + info-value (frozen anchors):** (a) `regret(hold_only) ≥ 2.0×regret(mechanism)` AND `regret(no_update) ≥ 2.0×regret(mechanism)`; (b) `regret(hold_only) ≥ 2.0×regret(random_active)`.
- **Tripwire (fail-closed, before verdict):** mechanism scored exploit(noop)-fraction ∈ (0.02, 0.98), AND no falsifier/ablation with exactly-0 delta across all seeds. Else `INSTRUMENT_INVALID` subtype `MECHANISM_INERT`.

## Verdict rule (frozen)
- `VOI_MECHANISM_PRESENT` iff G1a ∧ G1b ∧ G2 ∧ G3 ∧ G4a ∧ G4b ∧ G5 ∧ G6 ∧ tripwire-clear.
- `VOI_MECHANISM_PRESENT_UNCALIBRATED` iff all of the above except **G4a** fail — positive-but-weaker; drops the calibration sub-claim; `positive_claim: true` ⇒ STOP + FULL hostile audit. **(Expected outcome given q=0.004.)**
- `SIMPLE_ACTIVE_SUFFICIENT` iff G1b fails. `STATIC_SUFFICIENT` iff G1a fails but G1b passes.
- `ATTRIBUTION_FAILURE` (⇒ INSTRUMENT_INVALID) iff G1a ∧ G1b pass but the advantage **SURVIVES** a falsifier or uncertainty-ablation, where "survives" := `A_C` 95% CI **lower bound > 0** (still significantly better than the rivals after corruption). (This is the corrected definition; collapse-to-negative is NOT survival.)
- `INSTRUMENT_INVALID` iff G5 fails, G6 fails, tripwire fires, or seed-disjointness fails.
- `CAPABILITY_ABSENT` iff mechanism ≈ non-learning floors.

## Predeclared failure geography
Advantage present only for the full mechanism vs both rivals and on transfer; MUST collapse (to ≤ parity, i.e. `A_C` upper-CI ≤ 0) under wrong-sign, shuffled, and uncertainty-ablation; value-ablation must significantly reduce it. An advantage that stays significantly positive (`A_C` lower-CI > 0) under any falsifier/uncertainty-ablation ⇒ ATTRIBUTION_FAILURE. The mechanism MUST both noop and query. Calibration (G4a) expected to fail ⇒ `UNCALIBRATED` is the anticipated positive ceiling.

## Anti-rigging + anti-hardcoding (frozen)
Tuned static rival on a separate block; random-active + non-learning floors; oracle regret-0 + G6; single-constant q (no per-arm-drift access, NOT calibration-tuned); KG from belief only; corrected G2/G3 stated magnitude-free; **fresh scored/transfer seeds (9401–9430)**; env constants unchanged and not tuned; replayable from trace; no `v_i`/τ leak into observations/action-names/filenames/fixtures; no future observations; probe-first CPU budget STOP.

## Artifacts (ITL convention)
Under `artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-003A/`: `result.json` (verdict + subtype + per-rival/per-condition A tables + CIs + collapse/survive determinations + exploit-fraction + claim_ceiling + config_shas incl. this prereg), gate-scoped `trace.jsonl` + `metric_records.json`, `baseline_comparison.json`, `ablation_report.json`, `falsifier_report.json` (with the collapse-signature booleans), `calibration_transfer_report.json`, `replay_report.json`, `headroom_report.json`, `tripwire_report.json`, `failure_manifest.json` if any fail, `claim_ceiling.txt`. Card at `docs/task_cards/UNCERTAINTY-VOI-REQUEST-MECHANISM-003A.md`; code isolated under `src/uncertainty_voi/` (new `runner_003.py`; it MAY import the frozen simulation/policies from `runner_002.py` unchanged, and must implement only the corrected gate evaluation + verdict; do NOT edit `runner_002.py` or 002A/001A artifacts).
