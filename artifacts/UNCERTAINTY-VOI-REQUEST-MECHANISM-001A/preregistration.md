# PREREG FREEZE — UNCERTAINTY-VOI-REQUEST-MECHANISM-001A (intelligence-theory-lab)

> Ex-ante pre-registration. Repo: **intelligence-theory-lab** (NOT Ego — this is a lab mechanism testbed; the Ego pet capability lineage ends at #3 = "reflex + direct write, no update-gated adaptation"). All environment parameters, the mechanism, the tuned rival, seeds, metrics, thresholds, and the verdict rule below are **frozen at the commit that banks this file**. That commit MUST be an ancestor of the implementation and of any gated run it judges (commit order = ex-ante proof). Changing any frozen value requires a NEW prereg that is itself an ancestor of the re-run. **No post-hoc tuning.** Operator confirmed: run in intelligence-theory-lab; uncertainty representation / environment / claim ceiling delegated to Claude and frozen here. (All numeric gate thresholds — including the G4a calibration tolerance and the G6 floor-ratio / headroom-fraction — are pinned in this document ex-ante, before any run; there is no un-frozen threshold left to be set at implementation time.)

## Layer / claim ceiling (binding)
Layer 3 mechanism hypothesis. **Claim ceiling:** bounded offline evidence that ONE implemented uncertainty/value-of-information mechanism, in ONE toy environment, beats the best-tuned static-threshold rival on a VOI-headroom task distribution, and that this advantage collapses under wrong-sign feedback, shuffled feedback, and uncertainty-ablation, with a calibrating uncertainty estimate and held-out generalization. Proves NO general intelligence, real-world adaptation, world-modeling, understanding, self/agency/autonomy, subjectivity, emotion, consciousness, EGO/companion readiness, and specifically NOT that the pet has this mechanism. A PASS = a mechanism-proxy for uncertainty-driven VOI decision-making in a bounded toy.

## Environment (frozen) — restless Gaussian bandit with costly information
- `K = 8` arms. Episode horizon `H = 200` steps. Reward scale on [0,1] after squashing.
- Hidden value `v_i(t)` = Gaussian random walk: `v_i(t+1) = clip(v_i(t) + N(0, τ_i²), 0, 1)`. **Heterogeneous drift** (the VOI structure): 4 fast arms `τ_hi = 0.06`, 4 slow arms `τ_lo = 0.005` (assignment fixed per episode from the env-seed). Initial `v_i(0) ~ Uniform(0,1)`.
- Actions per step: `query(i)` (cost `c_q = 0.02`, returns `v_i(t) + N(0, σ_obs²)`, `σ_obs = 0.10`); `exploit` (cost 0, realizes reward `v_{argmax μ}(t)`; per-step regret `= max_j v_j(t) − v_chosen(t)`); `request` (cost `c_r = 0.08`, returns a lower-noise sample `v_i(t) + N(0, (σ_obs/3)²)` for the current top-2 arms by μ). One action per step.
- Primary outcome: **cumulative regret** over H (exploitation regret + information costs paid), lower = better. Paired across identical env instances (same env-seed ⇒ same value trajectories + noise draws) so all arms see the same world.

*(These constants are frozen. They were chosen for VOI headroom — heterogeneous drift + costly noisy info — not tuned to any result. G6 verifies headroom empirically; if the env turns out saturated, the verdict is INSTRUMENT_INVALID, not a silent re-tune.)*

## Mechanism under test (frozen) — Kalman belief + myopic VOI action rule
- **Belief**: per-arm `(μ_i, σ_i²)`, a Kalman filter over the random walk. Between steps: `σ_i² += q` (process/drift inflation, `q` = a single frozen constant `q = 0.004`, deliberately NOT the true per-arm τ_i² — the agent does not know which arms are fast; it must infer effective uncertainty from prediction error / observation recency). On a query/request sample `x` of arm i: `K = σ_i²/(σ_i²+σ_obs²)`, `μ_i += K(x−μ_i)`, `σ_i² *= (1−K)`. **Prediction error** `PE_i = |μ_i − x|` recorded (drives belief; large PE ⇒ Kalman gain already accounts for it — the PE is the innovation).
- **VOI action rule** (computed function of μ, σ, cost — NOT a fixed threshold): each step compute a myopic knowledge-gradient proxy `KG(a)` = expected reduction in one-step exploitation regret from info action `a`, using the belief (arms with high σ AND μ near the current max have high KG). Take `a* = argmax_a [KG(a) − cost(a)]` over {query(i)∀i, request}; if `max_a [KG(a)−cost(a)] ≤ 0`, `exploit`. Freeze the KG proxy: `KG(query i) = σ_i · φ(z_i)`-style expected-improvement over the incumbent max μ (z_i = (μ_i − μ_max_other)/σ_i); `KG(request) = Σ_{top2} σ_i·(1−1/3)` scaled. The exact closed form is in the impl; the frozen requirement is that the rule is a deterministic function of (μ, σ, cost) with no hidden-label access and no fixed PE/age threshold.

## Rival + controls (frozen)
- **RIVAL to beat (strong, tuned): `static_threshold`** — query the arm with the largest age-since-last-observation if `age > θ` (or PE>θ variant), else exploit; `request` never (or on a fixed period). `θ` (and the period) are **tuned by grid search on a SEPARATE tuning seed block (9301–9310)** to minimize regret, then frozen and evaluated on the scored seeds. This makes "static fails" a fair result. (A `static_threshold` that matches the mechanism on ONE seed is not a mechanism failure; a *control* matching it IS.)
- **CONTROLS that must NOT match (matching ⇒ INVALID):** `wrong_sign` (each sample reflected: `x' = 2μ_i − x`, so the innovation sign is flipped), `shuffled` (per episode, samples permuted across arms/time before the update), `uncertainty_ablation` (σ frozen to a constant ⇒ KG depends on μ only), `value_ablation` (KG ignores μ, uses σ only).
- **Floors:** `random_query`, `exploit_only`, `no_update`.
- **Ceiling:** `oracle` (knows `v_i(t)`, exploits argmax, pays no info cost) ⇒ regret 0 reference.

## Seeds (frozen; assert disjoint within task)
- Dev probe env-seed: `9001` (run first).
- Rival-tuning env-seeds: `9301–9310` (used ONLY to pick `θ`/period; never scored).
- Scored env-seeds: `M = 20`, `9101–9120`.
- Held-out transfer env-seeds: `9201–9210` (different drift schedule realization; forward-transfer test).
- Agent RNG: a single registered/seeded stream per run; no unseeded RNG. Assert the four blocks are pairwise disjoint; fail closed.

## Metrics + gates (thresholds frozen; CI/MDE-based, not magic numbers)
Primary statistic: **paired advantage** `A = regret(static_threshold) − regret(mechanism)` per env-seed (>0 ⇒ mechanism better). Report mean, 95% bootstrap CI (paired), and effect size, over the M=20 scored seeds. **MDE pre-registered: relative advantage ≥ 10% of static regret.**
- **G1 rival-beat**: mean `A > 0`, 95% CI excludes 0, AND mean relative advantage ≥ 10% (the MDE). (If underpowered — CI wide, straddles 0 — report `STATIC_SUFFICIENT` or increase M only via a NEW prereg.)
- **G2 falsifiers**: `A_wrong_sign` and `A_shuffled` each have 95% CI **including 0** (advantage collapses), AND `A_clean − A_falsified` CI excludes 0 (the collapse is significant).
- **G3 ablation**: `A_uncertainty_ablation` CI includes 0 (destroyed); `A_value_ablation` significantly < `A_clean` (value term load-bearing).
- **G4 calibration + transfer** (two sub-gates, both required for the unqualified positive verdict):
  - **G4a calibration** (numeric tolerance frozen ex-ante, NOT fitted): at each step `t`, for each arm `i`, form the standardized belief residual `z_i(t) = (μ_i(t) − v_i(t)) / σ_i(t)` from the agent's current posterior belief `(μ_i, σ_i²)` and the true hidden value `v_i(t)`. This is an **offline evaluation diagnostic** — it uses ground-truth `v_i` only for scoring, exactly like the oracle; the agent never sees `v_i`, so this is NOT label leakage into the model under test. A well-calibrated Kalman filter has `E[z²] = 1`. Pass iff the aggregate `mean(z_i(t)²)` over all scored (t,i) lies in **`[0.7, 1.5]`**. Secondary coverage check (reported, not gating): fraction of (t,i) with `|z_i(t)| ≤ 1.645` should lie in `[0.85, 0.95]` (nominal 90%).
  - **G4b transfer**: advantage on held-out transfer seeds `A_transfer` has 95% CI excluding 0.
- **G5 replay**: fresh-process ×2 bit-exact on all runs (RNG only via the seeded stream; AST rng-audit + fail-able positive control; gate-scoped trace + `metric_records` under the size cap — apply the trace-hygiene guard).
- **G6 headroom (anti-vacuity)** — thresholds frozen ex-ante, anchored to the random floor and the oracle, NOT to any observed result:
  - **(a) floor dominance**: `regret(random_query) ≥ 2.0 × regret(mechanism)` AND `regret(exploit_only) ≥ 2.0 × regret(mechanism)` (the mechanism is not ≈ a floor).
  - **(b) not-saturated / VOI headroom**: the tuned static rival is meaningfully suboptimal — `regret(static_threshold) − regret(oracle) ≥ 0.10 × [regret(random_query) − regret(oracle)]`. With `regret(oracle) = 0` this is `regret(static_threshold) ≥ 0.10 × regret(random_query)`, i.e. static captures at most 90% of the random→oracle span, leaving ≥10% headroom for a better VOI policy.
  - If either (a) or (b) fails — in particular if `static ≈ oracle` — ⇒ INSTRUMENT_INVALID (no VOI headroom — do not claim a win on a trivial env).

## Verdict rule (frozen)
- `VOI_MECHANISM_PRESENT` iff G1 ∧ G2 ∧ G3 ∧ G4a ∧ G4b ∧ G5 ∧ G6 all pass.
- `VOI_MECHANISM_PRESENT_UNCALIBRATED` iff G1 ∧ G2 ∧ G3 ∧ G4b ∧ G5 ∧ G6 all pass but **G4a (calibration) fails** — a positive-but-weaker outcome: the VOI advantage is real, transfers, and is attributable (collapses under falsifier and uncertainty-ablation), but the uncertainty estimate is outside the calibration tolerance, so the claim DROPS the "calibrating uncertainty estimate" clause. This is still a positive mechanism claim (`positive_claim: true`) ⇒ same STOP + Claude FULL hostile audit as `VOI_MECHANISM_PRESENT`.
- `STATIC_SUFFICIENT` iff G1 fails (mechanism does not beat the tuned static rival) — bounded negative, informative (a fixed threshold was enough on this env).
- `ATTRIBUTION_FAILURE` (⇒ INSTRUMENT_INVALID) iff G1 passes but the advantage survives a falsifier (G2 fails) or survives uncertainty-ablation (G3 fails) — the win is not VOI.
- `INSTRUMENT_INVALID` iff G5 fails, or G6 fails (saturated / no headroom), or seed-disjointness fails.
- `CAPABILITY_ABSENT` iff mechanism ≈ floors.

## Predeclared failure geography
Advantage MUST be absent (CI∋0) under wrong-sign, shuffled, uncertainty-ablation, and on a saturated env; present only for the full mechanism on the VOI-headroom distribution and on held-out transfer. Any advantage under falsifiers/ablation ⇒ INSTRUMENT_INVALID.

## Anti-rigging (frozen commitments)
Tuned (not strawman) static rival on a separate seed block; ideal/oracle regret-0 reference + G6 headroom check; the mechanism's `q` is a single constant (agent does NOT know per-arm drift — no hidden-label access); KG rule computed from belief only; thresholds pre-registered (incl. G4a `[0.7,1.5]` and G6 `2.0×` / `0.10×` anchors — no un-frozen threshold); replayable from trace; probe-first cost discipline (STOP if projection exceeds a pre-set CPU budget).

## Artifacts (ITL convention)
Under `artifacts/UNCERTAINTY-VOI-REQUEST-MECHANISM-001A/`: `result.json` (verdict + subtype + per-arm/per-condition A tables + CIs + claim_ceiling + config_shas incl. this prereg), gate-scoped `trace.jsonl` + `metric_records.json`, `baseline_comparison.json`, `ablation_report.json`, `falsifier_report.json`, `calibration_transfer_report.json` (G4a `mean(z²)` + coverage + G4b transfer CI), `replay_report.json`, `headroom_report.json` (G6 (a) floor ratios + (b) static/random/oracle regrets and the headroom fraction), `failure_manifest.json` if any fail. Card at `docs/task_cards/UNCERTAINTY-VOI-REQUEST-MECHANISM-001A.md`; code isolated under `src/uncertainty_voi/`; tests under `tests/`.
